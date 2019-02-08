# Python 2/3 compatibility
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *
from future.builtins.disabled import *
from future.standard_library import install_aliases
install_aliases()

from ._sddraft_extension import SDDraftExtension


class OgcMetadataExtensionMixin(SDDraftExtension):
    _ABSTRACT_KEY = "abstract"
    _ACCESS_CONSTRAINTS_KEY = "accessConstraints"
    _ADMINISTRATIVE_AREA_KEY = None
    _ADDRESS_KEY = None
    _CITY_KEY = "city"
    _COUNTRY_KEY = "country"
    _EMAIL_KEY = None
    _KEYWORD_KEY = "keyword"
    _FACSIMILE_KEY = None
    _FEES_KEY = "fees"
    _INDIVIDUAL_NAME_KEY = None
    _NAME_KEY = "name"
    _ORGANIZATION_KEY = None
    _PHONE_KEY = None
    _POSITION_NAME_KEY = None
    _POST_CODE_KEY = None
    _TITLE_KEY = "title"

    #region Properties

    @property
    def abstract(self):
        """Gets or sets the abstract of the service.

        :type: str
        """
        return self._get_prop_value(self._ABSTRACT_KEY)

    @abstract.setter
    def abstract(self, value):
        self._set_prop_value(self._ABSTRACT_KEY, value)

    @property
    def access_constraints(self):
        """Gets or sets a value indicating the legal constraints surrounding the use of the service.

        :type: str
        """
        return self._get_prop_value(self._ACCESS_CONSTRAINTS_KEY)

    @access_constraints.setter
    def access_constraints(self, value):
        self._set_prop_value(self._ACCESS_CONSTRAINTS_KEY, value)

    @property
    def administrative_area(self):
        """Gets or sets the administrative area (e.g. state, province) of the organization responsible for the WMS
        service.

        :type: str
        """
        return self._get_prop_value(self._ADMINISTRATIVE_AREA_KEY)

    @administrative_area.setter
    def administrative_area(self, value):
        self._set_prop_value(self._ADMINISTRATIVE_AREA_KEY, value)

    @property
    def address(self):
        """Gets or sets the address of the organization responsible for the service.

        :type: str
        """
        return self._get_prop_value(self._ADDRESS_KEY)

    @address.setter
    def address(self, value):
        self._set_prop_value(self._ADDRESS_KEY, value)

    @property
    def city(self):
        """Gets or sets the city metadata value for the service.

        :type: str
        """
        return self._get_prop_value(self._CITY_KEY)

    @city.setter
    def city(self, value):
        self._set_prop_value(self._CITY_KEY, value)

    @property
    def country(self):
        """Gets or sets the country metadata value for the service.

        :type: str
        """
        return self._get_prop_value(self._COUNTRY_KEY)

    @country.setter
    def country(self, value):
        self._set_prop_value(self._COUNTRY_KEY, value)

    @property
    def email(self):
        """Gets or sets the contact electronic mail value for the service.

        :type: str
        """
        return self._get_prop_value(self._EMAIL_KEY)

    @email.setter
    def email(self, value):
        self._set_prop_value(self._EMAIL_KEY, value)

    @property
    def facsimile(self):
        """Gets or sets the contact facsimile telephone value for the service.

        :type: str
        """
        return self._get_prop_value(self._FACSIMILE_KEY)

    @facsimile.setter
    def facsimile(self, value):
        self._set_prop_value(self._FACSIMILE_KEY, value)

    @property
    def fees(self):
        """Gets or sets a value describing the fees imposed when accessing the service.

        :type: str
        """
        return self._get_prop_value(self._FEES_KEY)

    @fees.setter
    def fees(self, value):
        self._set_prop_value(self._FEES_KEY, value)

    @property
    def individual_name(self):
        """Gets or sets the contact person value for the service.

        :type: str
        """
        return self._get_prop_value(self._INDIVIDUAL_NAME_KEY)

    @individual_name.setter
    def individual_name(self, value):
        self._set_prop_value(self._INDIVIDUAL_NAME_KEY, value)

    @property
    def keyword(self):
        """Gets or sets the keyword value for the service.

        :type: str
        """
        return self._get_prop_value(self._KEYWORD_KEY)

    @keyword.setter
    def keyword(self, value):
        self._set_prop_value(self._KEYWORD_KEY, value)

    @property
    def name(self):
        """Gets or sets the name of the service.

        :type: str
        """
        return self._get_prop_value(self._NAME_KEY)

    @name.setter
    def name(self, value):
        if value is None or value.strip() == "":
            raise ValueError("Name cannot be null or empty.")
        self._set_prop_value(self._NAME_KEY, value)

    @property
    def organization(self):
        """Gets or sets the contact organization value for the service.

        :type: str
        """
        return self._get_prop_value(self._ORGANIZATION_KEY)

    @organization.setter
    def organization(self, value):
        self._set_prop_value(self._ORGANIZATION_KEY, value)

    @property
    def phone(self):
        """Gets or sets the contact voice telephone value for the service.

        :type: str
        """
        return self._get_prop_value(self._PHONE_KEY)

    @phone.setter
    def phone(self, value):
        self._set_prop_value(self._PHONE_KEY, value)

    @property
    def position_name(self):
        """Gets or sets the name of the position for the contact for the service.

        :type: str
        """
        return self._get_prop_value(self._POSITION_NAME_KEY)

    @position_name.setter
    def position_name(self, value):
        self._set_prop_value(self._POSITION_NAME_KEY, value)

    @property
    def post_code(self):
        """Gets or sets the post code for the organization that provides the service.

        :type: int
        """
        return self._get_prop_value(self._POST_CODE_KEY)

    @post_code.setter
    def post_code(self, value):
        self._set_prop_value(
            self._POST_CODE_KEY,
            self._editor.verify_int(value, "post code", allow_zero=False))

    @property
    def title(self):
        """Gets or sets the title of the service.

        :type: str
        """
        return self._get_prop_value(self._TITLE_KEY)

    @title.setter
    def title(self, value):
        self._set_prop_value(self._TITLE_KEY, value)

    #endregion