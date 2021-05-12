<h1 align="center">Bobby Home</h1>

*<p align="center">Your open-source alarm. Leave your home with a peace of mind.</p>*

<p align="center">
  <a href="https://github.com/bobby-home/bobby-home/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat" /</a>
  <a href="https://github.com/bobby-home/bobby-home/blob/master/CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" /></a>
    <br>
    <a href="https://github.com/bobby-home/bobby-home/actions/workflows/tests.yml">
      <img src="https://github.com/bobby-home/bobby-home/actions/workflows/tests.yml/badge.svg" />
    </a>
    <a href="https://codecov.io/gh/bobby-home/bobby-home">
      <img src="https://codecov.io/gh/bobby-home/bobby-home/branch/master/graph/badge.svg?token=8VBGT298HB"/>
    </a>
    <br>
    <a href="https://app.netlify.com/sites/peaceful-leakey-b90c22/deploys">
      <img src="https://api.netlify.com/api/v1/badges/23f1a86a-e928-4c19-8139-959c1d307199/deploy-status"/>
    </a>
</p>

## Introduction
Bobby Home is an **open-source** software to protect your home from burglars without compromising your privacy.

It is primarily designed to run on a Raspberry Pi with PiCamera which makes the installation **affordable**.

This project is built from the ground up for simplicity, for developers and users, with a strong emphasis with your privacy first.

### Why?
- We all care about our homes and sadly burglaries could happen. That is why more and more companies sell alarms which are sometimes very expensive with very bad software in term of stability, user experience. Bobby is **affordable** and the software is so easy that your grandparent can use it.
- :eyes: Privacy matters. Alarm systems introduce cameras inside your home which could cause dramatic privacy flaws. With Bobby your data belong to you and only you, **all the data is only stored and processed locally**, on your Raspberry pi! *[1]*.
- :muscle: You can extend Bobby to connect it with all your IoT devices. Do you want to turn some lights on when a motion is detected? Close your stores? You can do anything you want thanks to Automations.
- :open_hands: Open-source is great. You can control and contribute to your alarm to improve it.

*[1] The only exception is Telegram which can be used to receive pictures and videos if motion is detected. But Telegram complies with our privacy rules.*

### Hardware
- Raspberry Pi 4 or 3 with at least 1gb of RAM. We recommand to have a Raspberry Pi 4 with 2gb of RAM.
- PiCamera *(or compatible camera)*. We use the picamera library to manage the camera so make sure your camera can be controled by this library.
- Raspberry Pi Zero if you want to bring remote cameras. For instance I have my Raspberry Pi 4 in my living room *(with a camera)* and a Raspberry Pi zero with a camera to monitore my courtyard.
- Any SD cards with a decent write/read speed otherwise your system will be slow with a capacity of 16gb at least. We recommand you to go with 32gb or even more if you feel it.
- A strong power supply for any of your Raspberry Pi. Go to their website and check their recommendations.
- :sound: Any speakers with jack connector if you want to make noise when people are detected. ⚠️ Don't power your speakers through the Raspberry Pi usb port it could lead to annoying noise. Go for a little power supply.

### :rocket: What is Bobby able to do?
Bobby is able to detect if somebody is present through PiCamera. Then it will:
- Send telegram message to alert you with a picture taken when the people has been detected and a video 10 seconds after the beginning. Then it will send you every minute a video until the people left or you switched off the alarm.
- (if created) Call Actions linked to Automations so you can interact with your IoT devices *(turn your lights on...)*.
- (if enabled) Play scary sound through Automations. We provide a service to play sound through speakers directly connected to your Raspberry Pi.

You can manage your alarm status by device through the following options:
- Web interface.
- Telegram bot through the command `/alarm`.
- Autopilot: create schedules to automatically turn off/on your alarm.

## :construction_worker: Status
This software is currently under active development.

It is currently deployed in 3 homes with a total of 5 cameras running without main issues.

## :books: Documentation
For developer documentation, visit [doc.bobby-home.com.](https://doc.bobby-home.com)

## Motivations
At the beginning, I wanted to secure my home because a lot of burglaries happened around in 2019-2020 near to me.
On the market today, we can find a lot of security cameras supposed to be intelligent and so on but I have a main concern: my privacy. I analyzed some security cameras, and I found some really bad things. For alarm systems sold by companies are expensive but still delivering a bad user experience. For example, my neighbors had a security system triggered by their dogs every night, so they lost almost a thousand euros.

So I decided to create everything myself. Sure a lot of open-source software exists, but they don't answer my need. I want something **simple** and these tools are badly designed, I could not understand easily the software to make my thing.

If you look at the code source of Bobby you will see that it's small and comprehensive but yet the system is powerful and fulfills the requirement of an alarm.

Then the project grew and here it is! I decided to go fully open-source.
