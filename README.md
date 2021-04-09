Documentation [![Netlify Status](https://api.netlify.com/api/v1/badges/23f1a86a-e928-4c19-8139-959c1d307199/deploy-status)](https://app.netlify.com/sites/peaceful-leakey-b90c22/deploys)
# Bobby Home
A simple and affordable way to install an alarm in your home without compromising your privacy.

Designed to run on Raspberry Pi boards.

[Read the documentation.](https://doc.bobby-home.com)

## Motivations
At the beginning, I wanted to secure my home. Basically, there have been a lot of burglaries around in 2019-2020.
On the market to day, we can find a lot of security cameras supposed to be intelligent and so on but I have a main concern: my privacy. I analyzed some security cameras, and I found some real bad things. So I decided to create everything myself. Sure a lot of open-source software exists, but... I don't want to be rude, but they are pretty bad designed, I could not understand easily the software to make my thing.

This project is build from the ground up for simplicity (for developers and users) and also privacy first.

## Features
### Alarm

| Feature        | Description                                                                                                                                                                                                                                                           | Status |
|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| Alarm status   | Allows the system to change the status of the alarm. If the status is running, then the system analyzes frames from the camera to detect either or not people(s) are detected. If the status is false, the camera does not send any frames thus does not analyze them. | beta   |
| Alarm schedule | Allows the system to change the status of the alarm based on schedules. Pick days, the time to start and the time to stop running the alarm.                                                                                                                          | beta   |

### Camera
| Feature                         | Description                                                                         | Status                      |
|---------------------------------|-------------------------------------------------------------------------------------|-----------------------------|
| PiCamera                        | Support for PiCamera.                                                               | beta                        |
| Video recording                 | Record video from a picamera, able to split the record.                             | beta                        |
| Camera object detection         | Analyzes frame to warn either or not people are detected. Uses the ROI if defined.  | beta                        |
| Camera Region Of Interest (ROI) | Allows the system to ignore objects that are not in the ROI defined by the resident | :warning: **experimental**  |
| Camera live stream              | Allows a resident to stream a camera (only one camera at the time).                 | :warning:  **experimental** |

:warning: Currently, we only support the PiCamera and no other usb camera or something else.


## Status
This software is currently under development, and we are discovering some bug's day to day.


It is currently deployed in 3 homes with a total of 5 cameras to test it in the real world, gather some data, and improve the overall!
