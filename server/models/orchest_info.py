# coding: utf-8

from __future__ import absolute_import

from typing import List, Dict  # noqa: F401

from server.models.base_model_ import Model
from server import util

class Orchest_Info(Model):

    def __init__(self, orchestration_id: str=None, sfc_id: str=None, sfc_name: str=None, status: str=None):

        self.swagger_types = {
            'orchestration_id': str,
            'sfc_id': str,
            'sfc_name': str,
            'status': str
        }

        self.attribute_map = {
            'orchestration_id': 'orchestration_id',
            'sfc_id': 'sfc_id',
            'sfc_name': 'sfc_name',
            'status': 'status'
        }

        self._orchestration_id = orchestration_id
        self._sfc_id = sfc_id
        self._sfc_name = sfc_name
        self._status = status

    @classmethod
    def from_dict(cls, dikt) -> 'Orchest_Info':
        return util.deserialize_model(dikt, cls)

    @property
    def orchestration_id(self) -> str:
        return self._orchestration_id

    @orchestration_id.setter
    def orchestration_id(self, orchestration_id: str):
        self._orchestration_id = orchestration_id

    @property
    def sfc_id(self) -> str:
        return self._sfc_id

    @sfc_id.setter
    def sfc_id(self, sfc_id: str):
        self._sfc_id = sfc_id

    @property
    def sfc_name(self) -> str:
        return self._sfc_name

    @sfc_name.setter
    def sfc_name(self, sfc_name: str):
        self._sfc_name = sfc_name

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status: str):
        self._status = status


