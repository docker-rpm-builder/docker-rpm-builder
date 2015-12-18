# I don't really like this but I don't seem to have a good option to setup testing log
# otherwise. We rely on the "singleton import" feature.


from drb.configure_logging import configure_root_logger
configure_root_logger(debug=True)
