import datetime
import typing
from unittest.mock import MagicMock

import pytest  # type: ignore

from redshift_connector.credentials_holder import (
    ABCAWSCredentialsHolder,
    ABCCredentialsHolder,
    AWSDirectCredentialsHolder,
    AWSProfileCredentialsHolder,
    CredentialsHolder,
)


@pytest.mark.parametrize("cred_holder", (AWSDirectCredentialsHolder, AWSProfileCredentialsHolder))
def test_aws_credentials_holder_inherit_from_abc(cred_holder) -> None:
    assert issubclass(cred_holder, ABCAWSCredentialsHolder)


def test_credentials_holder_inherits_from_abc() -> None:
    assert issubclass(CredentialsHolder, ABCCredentialsHolder)


def test_aws_direct_credentials_holder_should_have_session() -> None:
    mocked_session: MagicMock = MagicMock()
    obj: AWSDirectCredentialsHolder = AWSDirectCredentialsHolder(
        access_key_id="something",
        secret_access_key="secret",
        session_token="fornow",
        session=mocked_session,
    )

    assert isinstance(obj, ABCAWSCredentialsHolder)
    assert hasattr(obj, "get_boto_session")
    assert obj.has_associated_session == True
    assert obj.get_boto_session() == mocked_session


valid_aws_direct_credential_params: typing.List[typing.Dict[str, typing.Optional[str]]] = [
    {
        "access_key_id": "something",
        "secret_access_key": "secret",
        "session_token": "fornow",
    },
    {
        "access_key_id": "something",
        "secret_access_key": "secret",
        "session_token": None,
    },
]


@pytest.mark.parametrize("input", valid_aws_direct_credential_params)
def test_aws_direct_credentials_holder_get_session_credentials(input) -> None:
    input["session"] = MagicMock()
    obj: AWSDirectCredentialsHolder = AWSDirectCredentialsHolder(**input)

    ret_value: typing.Dict[str, str] = obj.get_session_credentials()

    assert len(ret_value) == 3 if input["session_token"] is not None else 2

    assert ret_value["aws_access_key_id"] == input["access_key_id"]
    assert ret_value["aws_secret_access_key"] == input["secret_access_key"]

    if input["session_token"] is not None:
        assert ret_value["aws_session_token"] == input["session_token"]


def test_aws_profile_credentials_holder_should_have_session() -> None:
    mocked_session: MagicMock = MagicMock()
    obj: AWSProfileCredentialsHolder = AWSProfileCredentialsHolder(profile="myprofile", session=mocked_session)

    assert isinstance(obj, ABCAWSCredentialsHolder)
    assert hasattr(obj, "get_boto_session")
    assert obj.has_associated_session == True
    assert obj.get_boto_session() == mocked_session


def test_aws_profile_credentials_holder_get_session_credentials() -> None:
    profile_val: str = "myprofile"
    obj: AWSProfileCredentialsHolder = AWSProfileCredentialsHolder(profile=profile_val, session=MagicMock())

    ret_value = obj.get_session_credentials()
    assert len(ret_value) == 1

    assert ret_value["profile"] == profile_val


@pytest.mark.parametrize(
    "expiration_delta",
    [
        datetime.timedelta(hours=3),  # expired 3 hrs ago
        datetime.timedelta(days=1),  # expired 1 day ago
        datetime.timedelta(weeks=1),  # expired 1 week ago
    ],
)
def test_is_expired_true(expiration_delta) -> None:
    credentials: typing.Dict[str, typing.Any] = {
        "AccessKeyId": "something",
        "SecretAccessKey": "secret",
        "SessionToken": "fornow",
        "Expiration": datetime.datetime.now(datetime.timezone.utc) - expiration_delta,
    }

    obj: CredentialsHolder = CredentialsHolder(credentials=credentials)

    assert obj.is_expired() == True


@pytest.mark.parametrize(
    "expiration_delta",
    [
        datetime.timedelta(minutes=2),  # expired 1 minute ago
        datetime.timedelta(hours=3),  # expired 3 hrs ago
        datetime.timedelta(days=1),  # expired 1 day ago
        datetime.timedelta(weeks=1),  # expired 1 week ago
    ],
)
def test_is_expired_false(expiration_delta) -> None:
    credentials: typing.Dict[str, typing.Any] = {
        "AccessKeyId": "something",
        "SecretAccessKey": "secret",
        "SessionToken": "fornow",
        "Expiration": datetime.datetime.now(datetime.timezone.utc) + expiration_delta,
    }

    obj: CredentialsHolder = CredentialsHolder(credentials=credentials)

    assert obj.is_expired() == False
