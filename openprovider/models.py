# coding=utf-8

"""
Wrapper classes for API models. Most of these are thin wrappers over lxml
objectified versions of API responses.
"""

import lxml.etree
from openprovider.util import snake_to_camel


class Model(object):
    """
    Superclass for all models. Delegates attribute access to a wrapped class.
    """

    def __init__(self, obj=None, **kwargs):
        self._obj = obj
        self.attrs = kwargs

    def __getattr__(self, attr):
        """
        Magic for returning an attribute. Will try the attributes of the
        wrapper class first, then attributes in self.attrs, then the attributes
        of the wrapped objectified element.

        Will try a camelCased version of the snake_cased input if the attribute
        contains an underscore. This means foo.company_name will return the same
        as foo.companyName.
        """

        if "_" in attr:
            attr = snake_to_camel(attr)

        if attr in self.__dict__:
            # Check ourselves first no avoid infinite loops
            return getattr(self, attr)
        elif attr in self.attrs:
            # Then check manual attributes from the constructor
            return self.attrs[attr]
        elif hasattr(self._obj, attr):
            # Finally check the wrapped object
            return getattr(self._obj, attr)
        else:
            # No match, raise a custom AttributeError.
            attr_keys = self.attrs.keys()

            if self._obj:
                obj_keys = [t.tag for t in self._obj.iterchildren()]
            else:
                obj_keys = []

            raise AttributeError("Model has no attribute '%s' (tried '%s')"
                                 % (attr, "', '".join(attr_keys + obj_keys)))

    def get_elem(self):
        """Returns the wrapped lxml element, if one exists, or else None."""
        return self._obj

    def dump(self, *args, **kwargs):
        """Dumps a representation of the Model on standard output."""
        lxml.etree.dump(self._obj, *args, **kwargs)


def submodel(klass, key):
    """Shortcut for defining a submodel (has-a relation)."""
    def getter(self):
        return klass(getattr(self._obj, key))
    return property(getter)


class Name(Model):
    """
    A person's name.

    initials (required)
        Initials (first letters of first names, first letter of last name)
    firstName (required)
        First name
    prefix (optional)
        Prefix (often occuring in Dutch names; for example van de)
    lastName (required)
        Last name
    """

    def __str__(self):
        if hasattr(self, "prefix"):
            return " ".join((self.firstName, self.prefix, self.lastName))
        else:
            return " ".join((self.firstName, self.lastName))


class Domain(Model):
    """
    A domain name.

    name (required)
        The domain name without extension
    extension (required)
        The extension part of the domain name
    """

    def __str__(self):
        return ".".join((self.name, self.extension))


class Nameserver(Model):
    """
    A nameserver with either an IPv4 or an IPv6 address.

    name (required)
        URI or hostname of the nameserver
    ip (required if no valid ip6)
        IPv4 address of the nameserver
    ip6 (required if no valid ip)
        IPv6 address of the nameserver
    """
    pass


class Record(Model):
    """
    A DNS record.

    type (required)
        One of the following data types: A, AAAA, CNAME, MX, SPF, TXT
    name (optional)
        The part of the hostname before the domainname; for example www or ftp
    value (required)
        The value of the record; depending on the type, certain restrictions
        apply; see the FAQ for these restrictions
    prio (optional)
        Priority of the record; required for MX records; ignored for all other
        record types
    ttl (required)
        The Time To Live of the record; this is a value in seconds
    """
    pass


class History(Model):
    """
    Representation of a single modification of a piece of data.

    date (required)
        Date of the modification
    was (required)
        Old contents of the record
    is (required)
        New contents of the record
    """
    pass


class Address(Model):
    """
    A physical street address.

    street (required)
    number (required)
    suffix (optional)
    zipcode (required)
    city (required)
    state (optional)
    country (required)
    """
    pass


class Phone(Model):
    """
    An international phone number.

    countryCode (required)
    areaCode (required)
    subscriberNumber (required)
    """

    def __str__(self):
        """Returns the parts of the phone number seperated by spaces."""
        fmt = " ".join((self.countryCode,
                        self.areaCode,
                        self.subscriberNumber))
        return fmt


class Reseller(Model):
    """
    A reseller profile.

    id
    companyName
    address
    phone
    fax
    vatperc
    balance
    reservedBalance
    """

    address = submodel(Address, "address")
    phone = submodel(Phone, "phone")
    fax = submodel(Phone, "fax")


class Customer(Model):
    """
    A customer.

    handle
    companyName
    vat
    name
    gender
    address
    phone
    fax
    email
    """

    address = submodel(Address, "address")
    phone = submodel(Phone, "phone")
    fax = submodel(Phone, "fax")


class SSLProduct(Model):
    """
    An SSL product.

    id
    name
    brandName
    category
    isMobileSupported
    isIdnSupported
    isSgcSupported
    isWildcardSupported
    isExtendedValidationSupported
    deliveryTime
    freeRefundPeriod
    freeReissuePeriod
    maxPeriod
    numberOfDomains
    encryption
    root
    warranty
    prices
    supportedSoftware
    description
    """
    pass


class SSLOrder(Model):
    """
    An ordered SSL certificate.

    id
    commonName
    productName
    brandName
    status
    orderDate
    activeDate
    expirationDate
    hostNames
    organizationHandle
    administrativeHandle
    technicalHandle
    billingHandle
    emailApprover
    csr
    certificate
    rootCertificate
    """
    pass


class Extension(Model):
    """
    A domain extension (TLD).

    name
    transferAvailable
    isTransferAuthCodeRequired
    domicileAvailable
    usageCount
    description
    prices
    isAuthorizationCodeRequired
    isLockingAllowed
    isTradeAllowed
    restorePrice
    """
    pass
