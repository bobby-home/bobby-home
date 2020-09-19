# MQTT Broker
I'm using the MQTT protocol to connect my different devices. I've made the choice to use Mosquitto MQTT Broker running on my raspberryPI,
but why? I could have use something like Amazon IoT. Let's see that!

# Why local MQTT Broker?
Using a local MQTT Broker is a little bit painful, at least compared to using something in the cloud plug & play. For example, you have to manage your certificates to have TLS and so one.
You also have to ensure a good availability because this service is the root of everything. Every IoT device will communicate through it.
No more MQTT Broker? No more home security!

## Reach the outside world
The system was designed in the first place to be installed in a small countryside in France, so internet problems happen. I have to ensure that the system works without outside internet.
If the system can't reach the outside world, at least everything's locally have to work, if someone breaks in the house, the alarm should be triggered.

## Availability issues
So yeah, I won't use any cloud service provider to support my MQTT Broker, so I will have to manage myself the service availability.
To do this, I will monitor this service very closely and have alerts if something's goes wrong.
*Because yes, you can do everything, something wrong will still happens at some time.*
