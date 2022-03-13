#include <bits/stdint-uintn.h>
#include <sstream>
#include <csignal>
#include <regex>
#include <iostream>
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <string>
#include <cstring>
#include <cctype>
#include <thread>
#include <chrono>
#include "mqtt/async_client.h"
#include <opencv2/opencv.hpp>
#include <vector>
#include <chrono>
#include <fmt/core.h>

#include <uuid/uuid.h>
#include "object_detect.hpp"
#include "tensorflow/lite/builtin_op_data.h"
#include "tensorflow/lite/c/common.h"
#include "tensorflow/lite/interpreter.h"
#include "tensorflow/lite/kernels/register.h"
#include <nlohmann/json.hpp>
using json = nlohmann::json;
#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest.h"

#include "object_detect.hpp"
#include "processing/object_detection.hpp"

using namespace std::chrono_literals;


inline const std::string CLIENT_ID = "bobby_cpp_objectdetection";

// last parameter is the device id
inline const std::string TOPIC = "ia/picture/+";
inline const std::regex TOPIC_REGEX("ia/picture/(.+)");

// last parameter is a reference, an event, uuid...
// it will answer with the same event, it's used to keep track of req/res.
inline const std::string PICTURE_TOPIC = "object-detection/picture/+";
inline const std::regex PICTURE_TOPIC_REGEX("object-detection/picture/(.+)");

inline const std::string OBJECT_DETECTION_RES_TOPIC = "object-detection/response";

const int	QOS = 1;
const int	N_RETRY_ATTEMPTS = 5;

std::string uuid_v4() {
    uuid_t uuidObj;
    uuid_generate(uuidObj);
    char str[100];
    uuid_unparse(uuidObj, str);
    std::string event_ref{str};
    // DON'T use this, it generated non-utf8 string.
    //std::string event_ref{ std::begin(uuidObj), std::end(uuidObj) };

    return event_ref;
}

struct MotionPayload {
    std::string event_ref;
    std::vector<Detection> detections;
    bool status = true;
};

struct NoMoreMotionPayload {
    std::string event_ref;
    bool status = false;
};

struct DetectionPayload {
    std::string event_ref;
    std::vector<Detection> detections;
};

// JSON PART
void to_json(json& j, const Detection& r)
{
    j = {
        {"score", r.confidence},
        {"class_id", r.name},
        {"x", r.x},
        {"y", r.y},
        {"w", r.width},
        {"h", r.height}
    };
}

void to_json(json& j, const MotionPayload& p)
{
    j = {
            {"status", p.status},
            {"event_ref", p.event_ref},
            {"detections", p.detections}
    };
}

void to_json(json& j, const NoMoreMotionPayload& p)
{
    j = {
            {"status", p.status},
            {"event_ref", p.event_ref},
            //{"detections", p.detections}
    };
}

void to_json(json& j, const DetectionPayload& p)
{
    j = {
            {"event_ref", p.event_ref},
            {"detections", p.detections}
    };
}
TEST_CASE("MotionPayload_to_json") {
    std::vector<Detection> detections = {};
    std::string event_ref = uuid_v4();

    SUBCASE("should work with motion payload") {
        Detection d(1, "people", 0.66, 4, 4, 4, 4);
        detections.push_back(d);
        MotionPayload payload = {event_ref, detections};
        json payload_json = payload;
        std::cout << "json to publish: " << payload_json << std::endl;
    }

    SUBCASE("should work with no more motion payload") {
        NoMoreMotionPayload payload = {event_ref};
        json payload_json = payload;
        std::cout << "json to publish: " << payload_json << std::endl;
    }
}

enum class State {
    TRIGGER_MOTION,
    TRIGGER_NO_MOTION,
    DO_NOTHING
};

class ObjectDetectionAnalyzer
{
public:
    ObjectDetectionAnalyzer(unsigned int nb_frame_up_threshold, unsigned int nb_frame_down_threshold)
    {
        std::cout << "init object detection analyzer" << std::endl;
        false_detection_ = 0;
        true_detection_ = 0;
        nb_frame_down_threshold_ = nb_frame_down_threshold;
        nb_frame_up_threshold_ = nb_frame_up_threshold;
    }

    State analyze(const std::vector<Detection> &detections)
    {
        if (detections.size() != 0)
        {
            true_detection_ = true_detection_ +1;
        }
        else if (true_detection_ > 0 || current_detection_)
        {
            false_detection_ = false_detection_ +1;
        }

        // make sure to have unpair number.
        // otherwise true_detection could be equal to false_detection_
        // if its the case, could be bad to make a decision if the threshold is based on < or > operator.

        unsigned int limit = current_detection_ ? nb_frame_down_threshold_ : nb_frame_up_threshold_;

        if (true_detection_ + false_detection_ == limit)
        {
            auto r = process_event_();
            std::cout << "true_detection_" << true_detection_ << " false=" << false_detection_ << std::endl;
            true_detection_ = 0;
            false_detection_ = 0;
            return r;
        }

        return State::DO_NOTHING;
    }
    std::string toString() const
    {
        return fmt::format(
                "true_detection = {} false_detection = {}, current_detection = {}",
                true_detection_, false_detection_, current_detection_
                );
    }
private:
    unsigned int nb_frame_up_threshold_;
    unsigned int nb_frame_down_threshold_;
    unsigned int true_detection_ = 0;
    unsigned int false_detection_ = 0;
    bool current_detection_ = false;

    State process_event_()
    {
        std::cout << "process event" << std::endl;
        if (current_detection_)
        {
            if (false_detection_ > true_detection_)
            {
                // end of motion.
                std::cout << "end of motion" << std::endl;
                current_detection_ = false;
                return State::TRIGGER_NO_MOTION;
            }
            std::cout << "somebody is still here" << std::endl;
            return State::DO_NOTHING;
        }
        else
        {
            if (false_detection_ < true_detection_)
            {
                std::cout << "trigger motion!" << std::endl;
                current_detection_ = true;
                return State::TRIGGER_MOTION;
            }

            // Nobody might be: people left quickly OR false positive detection.
            std::cout << "nobody true=" << true_detection_ << " false=" << false_detection_ << std::endl;
            return State::DO_NOTHING;
        }

    }
};

std::ostream& operator << (std::ostream &os, const ObjectDetectionAnalyzer &o) {
    return (os << o.toString() << std::endl);
}

#ifndef DOCTEST_CONFIG_DISABLE
State trigger_motion(bool motion, std::vector<Detection> &detections, ObjectDetectionAnalyzer &analyzer)
{
    State result;
    int modulo;
    int limit;

    if (motion) {
        limit = 3;
        modulo = 2;
    } else {
        limit = 9;
        modulo = 3;
    }

    for (int i = 0; i < limit; i++) {
        if (i % modulo == 0) {
            Detection d(1, "people", 0.66, 4, 4, 4, 4);
            detections.push_back(d);
            //std::cout << "analyze with motion" << std::endl;
        } else {
            detections.clear();
        }
        result = analyzer.analyze(detections);
    }

    return result;
}
#endif

TEST_CASE("ObjectDetectionAnalyzer_tests")
{
    ObjectDetectionAnalyzer analyzer(3, 9);
    std::vector<Detection> detections = {};

    SUBCASE("should do nothing") {
        std::vector<Detection> detections = {};
        for (int i = 0; i < 9; i++) {
            auto r = analyzer.analyze(detections);
            CHECK(r == State::DO_NOTHING);
        }
    }

    SUBCASE("should trigger motion") {
        auto r = trigger_motion(true, detections, analyzer);
        CHECK(r == State::TRIGGER_MOTION);
        CAPTURE(analyzer);
    }

    SUBCASE("should trigger no more motion") {
        trigger_motion(true, detections, analyzer);
        detections.clear();
        auto r = trigger_motion(false, detections, analyzer);
        CHECK(r == State::TRIGGER_NO_MOTION);
    }
}

struct DeviceObjectDetection {
    DeviceObjectDetection(std::string e, std::shared_ptr<ObjectDetectionAnalyzer> a, std::chrono::high_resolution_clock::time_point c, std::chrono::high_resolution_clock::time_point p) :
        current_motion_event_ref(e), analyzer(a), created_at(c), sent_ping_at(p) {}

    std::string current_motion_event_ref;
    std::shared_ptr<ObjectDetectionAnalyzer> analyzer;
    std::chrono::high_resolution_clock::time_point created_at;
    std::chrono::high_resolution_clock::time_point sent_ping_at;
};

class BobbyMQTTObjectDetection
{
public:
 	BobbyMQTTObjectDetection(mqtt::async_client& cli)
        : mqtt_client_(cli) {}

    std::string get_motion_topic(const std::string &device_id)
    {
        return fmt::format("motion/camera/{}", device_id);
    }

    std::string get_motion_picture_topic(const std::string &device_id, const std::string &event_ref, const bool motion)
    {
        return fmt::format("motion/picture/{}/{}/{}", device_id, event_ref, int(motion));
    }

    std::string get_ping_topic(const std::string &device_id)
    {
        return fmt::format("ping/object_detection/{}", device_id);
    }

    std::string get_object_detection_topic(const std::string &event_ref)
    {
        return fmt::format("{}/{}", OBJECT_DETECTION_RES_TOPIC, event_ref);
    }

    void trigger_detection_answer(const std::string &event_ref, std::vector<Detection> &detections, char* picture, size_t size)
    {
        DetectionPayload payload_obj = {event_ref, detections};
        json payload_json = payload_obj;
        std::string payload = payload_json.dump();

        std::cout << "detection_answer: json to publish: " << payload << std::endl;

        const std::string answer_topic = get_object_detection_topic(event_ref);
        mqtt::message_ptr pubmsg = mqtt::make_message(answer_topic, payload);
        fmt::print("publish to topic: {}\n", answer_topic);
        mqtt_client_.publish(pubmsg);
    }

    std::string trigger_motion(const std::string &device_id, std::vector<Detection> &detections, char* picture, size_t size)
    {
        fmt::print("");
        auto event_ref = uuid_v4();
        MotionPayload payload_obj = {event_ref, detections};
        json payload_json = payload_obj;
        std::string payload = payload_json.dump();


        auto motion_topic = get_motion_topic(device_id);
        mqtt::message_ptr pubmsg = mqtt::make_message(motion_topic, payload);
        fmt::print("trigger motion topic={} payload={}\n", motion_topic, payload);
        mqtt_client_.publish(pubmsg);

        auto picture_topic = get_motion_picture_topic(device_id, event_ref, true);
        pubmsg = mqtt::make_message(picture_topic, picture, size);
        pubmsg->set_qos(1);
        fmt::print("send motion picture topic={}\n", picture_topic);
        mqtt_client_.publish(pubmsg);

        return event_ref;
    }

    void send_ping(const std::string &device_id)
    {
        mqtt::message_ptr pubmsg = mqtt::make_message(get_ping_topic(device_id), "");
        pubmsg->set_qos(0);
        mqtt_client_.publish(pubmsg);
    }

    void trigger_no_motion(const std::string &device_id, const std::string &event_ref, std::vector<Detection> &detections, char* picture, size_t size)
    {
        if (event_ref.empty())
        {
            // seatbelt, it should not happen...
            // monitore this logs to create alerts!
            std::cerr << "can't trigger no motion without event_ref. This should not happen!" << std::endl;
            return;
        }

        NoMoreMotionPayload payload_obj = {event_ref};
        json payload_json = payload_obj;
        std::string payload = payload_json.dump();

        std::cout << "trigger no motion: json to publish: " << payload << std::endl;
        mqtt::message_ptr pubmsg = mqtt::make_message(get_motion_topic(device_id), payload);
        pubmsg->set_qos(2);
        mqtt_client_.publish(pubmsg);

        std::cout << "send picture" << std::endl;
        pubmsg = mqtt::make_message(get_motion_picture_topic(device_id, event_ref, false), picture, size);
        pubmsg->set_qos(1);
        mqtt_client_.publish(pubmsg);
    }

private:
    mqtt::async_client& mqtt_client_;
};

class BobbyObjectDetection
{
public:
	BobbyObjectDetection(
            BobbyMQTTObjectDetection& cli,
            ObjectDetection& object_detection,
            unsigned int nb_frame_up_threshold,
            unsigned int nb_frame_down_threshold
        ) : mqtt_client_(cli),
            object_detection_(object_detection),
            nb_frame_up_threshold_(nb_frame_up_threshold),
            nb_frame_down_threshold_(nb_frame_down_threshold) {}

    /**
     * Process frame video uses an algorithm to decide either or not the object should be considered,
     * and thus publish the event.
     * It's done because we send multiple frames (video), and it reduces a little bit our false positive events.
     * So, no every frame will receive an answer.
     * -> publish first frame. No answer.
     * -> ...
     * -> people is considered as a threat -> trigger.
     *  Same thing when people is not detected anymore to avoid to trigger/untrigger too quickly.
     */
    void process_frame_video(const std::string &device_id, std::vector<Detection> &detections, char* picture, size_t payload_size)
    {
        auto device = get_device_(device_id);

        fmt::print("device analyzer before analyze {}\n", device->analyzer->toString());
        fmt::print("detections size: {}\n", detections.size());
        auto todo = device->analyzer->analyze(detections);
        fmt::print("device analyzer after analyze {}\n", device->analyzer->toString());

        switch (todo) {
            case State::DO_NOTHING:
                std::cout << "do nothing, lazy boy!" << std::endl;
                break;
            case State::TRIGGER_MOTION:
            {
                std::cout << "alert alert alert!" << std::endl;
                auto event_ref = mqtt_client_.trigger_motion(device_id, detections, picture, payload_size);
                device->current_motion_event_ref = event_ref;
                break;
            }
            case State::TRIGGER_NO_MOTION:
                std::cout << "stop the alert" << std::endl;
                mqtt_client_.trigger_no_motion(device_id, device->current_motion_event_ref, detections, picture, payload_size);
                device->current_motion_event_ref = "";
                break;
            default:
                std::cerr << "Cannot handle state " << std::endl;
        }

        if (is_ping_necessary_(device_id))
        {
            mqtt_client_.send_ping(device_id);
            std::cout << "sending ping" << std::endl;
        }
    }

    void process_frame(const std::string topic, char* data, size_t payload_size)
    {
        cv::Mat raw_data(1, payload_size, CV_8UC1, data);
        cv::Mat decoded_img = cv::imdecode(raw_data, cv::IMREAD_COLOR);
        if (decoded_img.empty())
        {
            std::cerr << "error in imdecode, empty image" << std::endl;
            return;
        }
        std::vector<Detection> detections;
        object_detection_.runInference(decoded_img, detections);

        std::smatch base_match;

        if (std::regex_match(topic, base_match, PICTURE_TOPIC_REGEX))
        {
            // The first sub_match is the whole string; the next
            // sub_match is the first parenthesized expression.
            if (base_match.size() == 2)
            {
                std::ssub_match base_sub_match = base_match[1];
                std::string event_ref = base_sub_match.str();
                // Process frame instant publishes the answer to the MQTT topic for every frame it receives.
                mqtt_client_.trigger_detection_answer(event_ref, detections, data, payload_size);
            }
        }
        else if (std::regex_match(topic, base_match, TOPIC_REGEX))
        {
            // The first sub_match is the whole string; the next
            // sub_match is the first parenthesized expression.
            if (base_match.size() == 2)
            {
                std::ssub_match base_sub_match = base_match[1];
                std::string device_id = base_sub_match.str();

                detections.erase(
                    std::remove_if (detections.begin(), detections.end(), [](Detection const detection) { return detection.name != "person"; }),
                    detections.end());

                process_frame_video(device_id, detections, data, payload_size);
            }

        }
        else
        {
            fmt::print(stderr, "topic: {} unrecognizable.", topic);
        }
    }

private:
    unsigned int nb_frame_up_threshold_;
    unsigned int nb_frame_down_threshold_;
    BobbyMQTTObjectDetection &mqtt_client_;
    ObjectDetection& object_detection_;
    std::unordered_map<std::string, std::shared_ptr<DeviceObjectDetection>> devices_;

    bool is_ping_necessary_(const std::string &device_id)
    {
        auto device_it = devices_.find(device_id);
        if (device_it != devices_.end()) {
            auto device = device_it->second;
            auto end = std::chrono::high_resolution_clock::now();
            double elapsed_time_ms = std::chrono::duration<double, std::milli>(end - device->sent_ping_at).count();

            if ((elapsed_time_ms / 1000) >= 60)
            {
                device->sent_ping_at = std::chrono::high_resolution_clock::now();
                return true;
            }
            return false;
        }

        std::cerr << "is_ping_necessary_ device_id not found " << device_id << std::endl;
        return false;
    }

    std::shared_ptr<DeviceObjectDetection> get_device_(const std::string &device_id)
    {
        auto device_it = devices_.find(device_id);
        if (device_it != devices_.end()) {
            auto device = device_it->second;

            auto end = std::chrono::high_resolution_clock::now();
            auto ago = std::chrono::duration_cast<std::chrono::milliseconds>(end - device->created_at).count();
            fmt::print("found device {} created {} seconds ago.\n", device_id, ago);

            return device;
        }
        std::cout << "creating resources for device " << device_id << std::endl;

        auto analyzer = std::make_shared<ObjectDetectionAnalyzer>(nb_frame_up_threshold_, nb_frame_down_threshold_);
        std::string event_ref = "";

        auto new_device = std::make_shared<DeviceObjectDetection>(
                event_ref,
                analyzer,
                std::chrono::high_resolution_clock::now(),
                std::chrono::high_resolution_clock::now()
        );
        devices_.insert(std::make_pair(device_id, new_device));

        return new_device;
    }
};

/////////////////////////////////////////////////////////////////////////////

// Callbacks for the success or failures of requested actions.
// This could be used to initiate further action, but here we just log the
// results to the console.

class ActionListener : public virtual mqtt::iaction_listener
{
	std::string name_;

	void on_failure(const mqtt::token& tok) override {
		std::cout << name_ << " failure";
		if (tok.get_message_id() != 0)
			std::cout << " for token: [" << tok.get_message_id() << "]" << std::endl;
		std::cout << std::endl;
	}

	void on_success(const mqtt::token& tok) override {
		std::cout << name_ << " success";
		if (tok.get_message_id() != 0)
			std::cout << " for token: [" << tok.get_message_id() << "]" << std::endl;
		auto top = tok.get_topics();
		if (top && !top->empty())
			std::cout << "\ttoken topic: '" << (*top)[0] << "', ..." << std::endl;
		std::cout << std::endl;
	}

public:
	ActionListener(const std::string& name) : name_(name) {}
};

/////////////////////////////////////////////////////////////////////////////

/**
 * Local callback & listener class for use with the client connection.
 * This is primarily intended to receive messages, but it will also monitor
 * the connection to the broker. If the connection is lost, it will attempt
 * to restore the connection and re-subscribe to the topic.
 */
class Callback : public virtual mqtt::callback,
					public virtual mqtt::iaction_listener

{
public:
	Callback(mqtt::async_client& cli, mqtt::connect_options& connOpts, BobbyObjectDetection& bobby_objd)
				: nretry_(0), mqtt_client_(cli), connOpts_(connOpts), subListener_("Subscription"), object_detection_(bobby_objd) {
	}
protected:
	// Counter for the number of connection retries
	int nretry_;
	// The MQTT client
	mqtt::async_client& mqtt_client_;
	// Options to use if we need to reconnect
	mqtt::connect_options& connOpts_;
	// An action listener to display the result of actions.
	ActionListener subListener_;

	BobbyObjectDetection& object_detection_;

	// This deomonstrates manually reconnecting to the broker by calling
	// connect() again. This is a possibility for an application that keeps
	// a copy of it's original connect_options, or if the app wants to
	// reconnect with different options.
	// Another way this can be done manually, if using the same options, is
	// to just call the async_client::reconnect() method.
	void reconnect() {
		std::this_thread::sleep_for(std::chrono::milliseconds(2500));
		try {
			mqtt_client_.connect(connOpts_, nullptr, *this);
		}
		catch (const mqtt::exception& exc) {
			std::cerr << "Error: " << exc.what() << std::endl;
			exit(1);
		}
	}

	// Re-connection failure
	void on_failure(const mqtt::token& tok) override {
		std::cout << "Connection attempt failed" << std::endl;
		if (++nretry_ > N_RETRY_ATTEMPTS)
			exit(1);
		reconnect();
	}

	// (Re)connection success
	// Either this or connected() can be used for callbacks.
	void on_success(const mqtt::token& tok) override {}

	// (Re)connection success
	void connected(const std::string& cause) override {
		std::cout << "\nConnection success" << std::endl;
		std::cout << "\nSubscribing to topic '" << TOPIC << "'\n"
			<< "\tfor client " << CLIENT_ID
			<< " using QoS" << QOS << "\n"
			<< "\nPress Q<Enter> to quit\n" << std::endl;

		mqtt_client_.subscribe(TOPIC, QOS, nullptr, subListener_);
		mqtt_client_.subscribe(PICTURE_TOPIC, QOS, nullptr, subListener_);
	}

	// Callback for when the connection is lost.
	// This will initiate the attempt to manually reconnect.
	void connection_lost(const std::string& cause) override {
		std::cout << "\nConnection lost" << std::endl;
		if (!cause.empty())
			std::cout << "\tcause: " << cause << std::endl;

		std::cout << "Reconnecting..." << std::endl;
		nretry_ = 0;
		reconnect();
	}

	// Callback for when a message arrives.
	void message_arrived(mqtt::const_message_ptr msg) override {
		std::cout << "Message arrived" << std::endl;
		std::cout << "\ttopic: '" << msg->get_topic() << "'" << std::endl;

        auto payload = msg->get_payload();
        size_t payload_size = payload.size();
        char *data = payload.data();

        object_detection_.process_frame(msg->get_topic(), data, payload_size);
	}

	void delivery_complete(mqtt::delivery_token_ptr token) override {}
};

/////////////////////////////////////////////////////////////////////////////

int test_main(int argc, char* argv[])
{
    doctest::Context context;

    // !!! THIS IS JUST AN EXAMPLE SHOWING HOW DEFAULTS/OVERRIDES ARE SET !!!

    // defaults
    context.addFilter("test-case-exclude", "*math*"); // exclude test cases with "math" in their name
    context.setOption("abort-after", 5);              // stop test execution after 5 failed assertions
    context.setOption("order-by", "name");            // sort the test cases by their name

    context.applyCommandLine(argc, argv);

    // overrides
    context.setOption("no-breaks", true);             // don't break in the debugger when assertions fail

    int res = context.run(); // run

    if(context.shouldExit()) // important - query flags (and --exit) rely on the user doing this
        return res;          // propagate the result of the tests

    int client_stuff_return_code = 0;
    // your program - if the testing framework is integrated in your production code

    return res + client_stuff_return_code; // the result from doctest is propagated here as well
}

volatile std::sig_atomic_t stop;

void signal_handler(int signal)
{
    fmt::print(stdout, "got signal {}. Stopping the application.");
    stop = 1;
}

int main(int argc, char* argv[])
{
    std::signal(SIGINT, signal_handler);
    if (argc != 3) {
        fmt::print(stderr, "usage: {} <labels_file> <model_file>", argv[0]);
        exit(1);
    }

    std::string labels_file(argv[1]);
    std::string model_file(argv[2]);

    // Get necessary env variables.
    const char* mqtt_server = std::getenv("MQTT_SERVER");
    const char* mqtt_user = std::getenv("MQTT_USER");
    const char* mqtt_password = std::getenv("MQTT_PASSWORD");

    const char* up = std::getenv("NB_FRAME_UP_THRESHOLD");
    const char* down = std::getenv("NB_FRAME_DOWN_THRESHOLD");

    if (mqtt_server == NULL || mqtt_user == NULL || mqtt_password == NULL || up == NULL || down == NULL) {
        fmt::print(stderr, "missing an env variable.");
        exit(1);
    }

    // I know it's not great but hell :)
    unsigned int up_threshold;
    unsigned int down_threshold;

    std::stringstream up_s(up);
    std::stringstream up_d(down);
    up_s >> up_threshold;
    up_d >> down_threshold;

    fmt::print("up_threshold={} & down_threshold={}", up_threshold, down_threshold);

    // A subscriber often wants the server to remember its messages when its
	// disconnected. In that case, it needs a unique ClientID and a
	// non-clean session.
	mqtt::async_client mqtt_client(mqtt_server, CLIENT_ID);

    mqtt::connect_options connOpts = mqtt::connect_options_builder()
        .clean_session(false)
        .automatic_reconnect(true)
        .keep_alive_interval(std::chrono::seconds(30))
        .user_name(mqtt_user)
        .password(mqtt_password)
        .finalize();

    ObjectDetection object_detection(300, 300, labels_file, model_file);
    BobbyMQTTObjectDetection bobby_client(mqtt_client);
    BobbyObjectDetection bobby_object_detection(bobby_client, object_detection, up_threshold, down_threshold);

    // Install the callback(s) before connecting.
	Callback cb(mqtt_client, connOpts, bobby_object_detection);
	mqtt_client.set_callback(cb);

	// Start the connection.
	// When completed, the callback will subscribe to topic.

        try {
            std::cout << "Connecting to the MQTT server..." << std::flush;
            mqtt::token_ptr conntok = mqtt_client.connect(connOpts, nullptr, cb);
            std::cout << "Waiting for the connection..." << std::endl;
            conntok->wait();
            std::cout << "  ...OK" << std::endl;
        }
        catch (const mqtt::exception& exc) {
            std::cerr << "\nERROR: Unable to connect to MQTT server "
                << exc << std::endl;
        }

	// Just block till user tells us to quit.
    // todo: get Ctrl+c event to be nice with Docker.
	while (stop == 0) {
        std::this_thread::sleep_for(50ms);
    }

	// Disconnect
	try {
		std::cout << "\nDisconnecting from the MQTT server..." << std::flush;
		mqtt_client.disconnect()->wait();
		std::cout << "OK" << std::endl;
	}
	catch (const mqtt::exception& exc) {
		std::cerr << exc << std::endl;
        return 1;
	}

 	return 0;
}
