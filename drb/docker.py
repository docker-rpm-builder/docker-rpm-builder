from drb.which import which
from drb.dbc import precondition
from drb.spawn import sp
import os

class Docker(object):
    def __init__(self,  docker_exec=which("docker")):
        self._docker_exec = docker_exec
        self._options = []
        self._image = None
        self._cmd_and_args = None

    def run(self):
        precondition(self._image is not None, "image must be set")
        precondition(self._cmd_and_args is not None, "cmd_and_args must be set")
        # we're using an additional indirection level which might just be unuseful.
        # TODO: check bash escaping.
        sp("{docker_exec} run {options} {image} {cmd_and_args}", docker_exec=self._docker_exec,
           options=" ".join(self._options), image=self._image, cmd_and_args=" ".join(self._cmd_and_args))

    def image(self, image):
        self._image = image
        return self

    def cmd_and_args(self, *caa):
        self._cmd_and_args = caa
        return self

    def rm(self):
        self._options.append("--rm")
        return self

    def bindmount(self, host_dir, guest_dir, read_only=True):
        precondition(os.access(host_dir, os.R_OK | os.X_OK), "host_dir must be readable and executable")
        precondition(os.path.isabs(guest_dir), "guest_dir must be absolute")

        option = "--volume={0}:{1}{2}".format(os.path.abspath(host_dir), guest_dir, ("", ":ro")[read_only])
        self._options.append(option)
        return self

    def workdir(self, guest_dir):
        precondition(os.path.isabs(guest_dir), "guest_dir must be absolute")

        option = "--workdir={0}".format(guest_dir)
        self._options.append(option)
        return self




