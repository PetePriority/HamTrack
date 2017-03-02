# HamTrack
`HamTrack` is a tracking software that tracks your Hamster's nightly running activity. It measures revolutions of your Hamster's wheel using a [reed switch](https://en.wikipedia.org/wiki/Reed_switch), for example from a bike tachometer, that is connected to a GPIO pin. After a session is complete, it writes the data into a MySQL database and sends a Firebase Cloud message

# Requirements
`HamTrack` requires the python modules `rpi.gpio`, `pyfcm`, `peewee`, and `mysqlclient`

    pip install rpi.gpio pyfcm peewee mysqlclient

# Getting started
Adjust the configuration, in particular your wheel's circumference, mysql connection parameters, etc., and comment out features you don't need, like the Firebase Cloud messaging.

# PHP-script
The PHP-script, found in `php/`, requires the composer modules `twig` and `php-units-of-measure`. It displays daily, monthly, and session statistics. [This](https://sonic.serveftp.com/herbert/) shows it in action.
