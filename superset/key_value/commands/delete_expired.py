# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import logging
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from superset import db
from superset.commands.base import BaseCommand
from superset.key_value.exceptions import KeyValueDeleteFailedError
from superset.key_value.models import KeyValueEntry

logger = logging.getLogger(__name__)


class DeleteExpiredKeyValueCommand(BaseCommand):
    resource: str

    def __init__(self, resource: str):
        """
        Delete all expired key-value pairs

        :param resource: the resource (dashboard, chart etc)
        :return: was the entry deleted or not
        """
        self.resource = resource

    def run(self) -> None:
        try:
            self.delete_expired()
        except SQLAlchemyError as ex:
            db.session.rollback()
            logger.exception("Error running delete command")
            raise KeyValueDeleteFailedError() from ex

    def validate(self) -> None:
        pass

    @staticmethod
    def delete_expired() -> None:
        (
            db.session.query(KeyValueEntry)
            .filter(KeyValueEntry.expires_on <= datetime.now())
            .delete()
        )
        db.session.commit()
