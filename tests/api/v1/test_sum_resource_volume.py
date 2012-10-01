# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Test getting the total resource volume.
"""

import datetime
import logging

from ming import mim
from nose.plugins import skip

from ceilometer import counter
from ceilometer import meter

from ceilometer.tests import api as tests_api


class TestSumResourceVolume(tests_api.TestBase):

    def setUp(self):
        super(TestSumResourceVolume, self).setUp()

        # NOTE(dhellmann): mim requires spidermonkey to implement the
        # map-reduce functions, so if we can't import it then just
        # skip these tests unless we aren't using mim.
        try:
            import spidermonkey
        except:
            if isinstance(self.conn.conn, mim.Connection):
                raise skip.SkipTest('requires spidermonkey')

        self.counters = []
        for i in range(3):
            c = counter.Counter(
                'source1',
                'volume_size',
                'absolute',
                5 + i,
                'user-id',
                'project1',
                'resource-id',
                timestamp=datetime.datetime(2012, 9, 25, 10 + i, 30 + i),
                duration=0,
                resource_metadata={'display_name': 'test-volume',
                                   'tag': 'self.counter',
                                   }
                )
            self.counters.append(c)
            msg = meter.meter_message_from_counter(c)
            self.conn.record_metering_data(msg)

    def test_no_time_bounds(self):
        data = self.get('/resources/resource-id/meters/volume_size/volume/sum')
        expected = {'volume': 5 + 6 + 7}
        assert data == expected

    def test_start_timestamp(self):
        data = self.get('/resources/resource-id/meters/volume_size/volume/sum',
                        start_timestamp='2012-09-25T11:30:00')
        expected = {'volume': 6 + 7}
        assert data == expected

    def test_start_timestamp_after(self):
        data = self.get('/resources/resource-id/meters/volume_size/volume/sum',
                        start_timestamp='2012-09-25T12:34:00')
        expected = {'volume': None}
        assert data == expected

    def test_end_timestamp(self):
        data = self.get('/resources/resource-id/meters/volume_size/volume/sum',
                        end_timestamp='2012-09-25T11:30:00')
        expected = {'volume': 5}
        assert data == expected

    def test_end_timestamp_before(self):
        data = self.get('/resources/resource-id/meters/volume_size/volume/sum',
                        end_timestamp='2012-09-25T09:54:00')
        expected = {'volume': None}
        assert data == expected

    def test_start_end_timestamp(self):
        data = self.get('/resources/resource-id/meters/volume_size/volume/sum',
                        start_timestamp='2012-09-25T11:30:00',
                        end_timestamp='2012-09-25T11:32:00')
        expected = {'volume': 6}
        assert data == expected