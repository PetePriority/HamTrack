# HamTrack
`HamTrack` is a tracking software that tracks your Hamster's nightly running activity. It measures revolutions of your Hamster's wheel using a reed switch connected to a GPIO pin. After a session is complete, it writes the data into a MySQL database and sends a Firebase Cloud message

# Requirements
`HamTrack` requires the python modules `rpi.gpio`, `pyfcm`, `peewee`, and `mysqlclient`

    pip install rpi.gpio pyfcm peewee mysqlclient

# Getting started
Adjust the configuration, in particular your wheel's circumference, mysql connection parameters, etc., and comment out features you don't need, like the Firebase Cloud messaging.