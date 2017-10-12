# coding: utf-8
from mte.orm import ServiceEntity
import requests


class Service(ServiceEntity):
    def __init__(self, session=None):
        hostname = None  # config.CASHLOAN_HOSTNAME
        if session is None:
            session = requests.session()
        super(Service, self).__init__(session=session, hostname=hostname)
        self.session = session
