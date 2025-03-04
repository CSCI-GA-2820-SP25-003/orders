######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Base class for model
"""

from unittest.mock import patch
import pytest
from service.models.persistent_base import PersistentBase
from service.common.error_handlers import DataValidationError


@pytest.fixture
def persistent_instance():
    """Fixture to create and return a persistent_base instance"""
    instance = PersistentBase()
    instance.id = 1
    return instance


def test_update_raises_exception(persistent_instance):
    """Test that the update method raises an exception when commit fails"""
    # Patch db.session.commit to raise an exception
    with patch(
        "service.models.db.session.commit", side_effect=Exception("DB Commit Error")
    ):
        # Patch db.session.rollback to verify it's called when an exception occurs
        with patch("service.models.db.session.rollback") as mock_rollback:
            # Check if DataValidationError is raised and capture exception info
            with pytest.raises(DataValidationError) as excinfo:
                persistent_instance.update()

            # Ensure that rollback was called once after the exception
            mock_rollback.assert_called_once()

            # Ensure that the exception message contains the commit error message
            assert "DB Commit Error" in str(excinfo.value)
