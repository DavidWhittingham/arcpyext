import pytest

@pytest.mark.parametrize(("abstract"), [
    ("This is a test map service abstract. It could theoretically be quite long.")
])
def test_abstract(server_ext, abstract):
    assert isinstance(type(server_ext).abstract, property) == True
    server_ext.abstract = abstract
    assert server_ext.abstract == abstract

@pytest.mark.parametrize(("access_constraints"), [
    ("Do Not Distribute.")
])
def test_access_constraints(server_ext, access_constraints):
    assert isinstance(type(server_ext).access_constraints, property) == True
    server_ext.access_constraints = access_constraints
    assert server_ext.access_constraints == access_constraints

@pytest.mark.parametrize(("state"), [
    ("Fakeland")
])
def test_administrative_area(server_ext, state):
    assert isinstance(type(server_ext).administrative_area, property) == True
    server_ext.administrative_area = state
    assert server_ext.administrative_area == state

@pytest.mark.parametrize(("address"), [
    ("1 Fake St.")
])
def test_address(server_ext, address):
    server_ext.address = address
    assert server_ext.address == address

@pytest.mark.parametrize(("city"), [
    ("Faketown")
])
def test_city(server_ext, city):
    assert isinstance(type(server_ext).city, property) == True
    server_ext.city = city
    assert server_ext.city == city

@pytest.mark.parametrize(("country"), [
    ("Democratic Republic of FooBar")
])
def test_country(server_ext, country):
    server_ext.country = country
    assert server_ext.country == country

@pytest.mark.parametrize(("email"), [
    ("foo@bar.com")
])
def test_email(server_ext, email):
    assert isinstance(type(server_ext).email, property) == True
    server_ext.email = email
    assert server_ext.email == email

@pytest.mark.parametrize(("phone_number"), [
    ("+111 1111 1111")
])
def test_facsimile(server_ext, phone_number):
    assert isinstance(type(server_ext).facsimile, property) == True
    server_ext.facsimile = phone_number
    assert server_ext.facsimile == phone_number

@pytest.mark.parametrize(("name"), [
    ("Fake Person")
])
def test_individual_name(server_ext, name):
    assert isinstance(type(server_ext).individual_name, property) == True
    server_ext.individual_name = name
    assert server_ext.individual_name == name

@pytest.mark.parametrize(("organization"), [
    ("FooBar Corp.")
])
def test_organization(server_ext, organization):
    assert isinstance(type(server_ext).organization, property) == True
    server_ext.organization = organization
    assert server_ext.organization == organization

@pytest.mark.parametrize(("phone_number"), [
    ("+111 1111 1111")
])
def test_phone(server_ext, phone_number):
    assert isinstance(type(server_ext).phone, property) == True
    server_ext.phone = phone_number
    assert server_ext.phone == phone_number

@pytest.mark.parametrize(("position"), [
    ("Fake Position")
])
def test_position_name(server_ext, position):
    assert isinstance(type(server_ext).position_name, property) == True
    server_ext.position_name = position
    assert server_ext.position_name == position