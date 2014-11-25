# -*- coding: utf-8 -*-
# straight from http://pydenji.franzoni.eu . Didn't want to enlarge dependencies right now.

from urlparse import urlparse, uses_netloc
from pkg_resources import resource_filename, Requirement

#TODO: remove this sort of "static initializer"
if "pkg" not in uses_netloc:
    uses_netloc.append("pkg")

def file_uri_resolver(parsed_uri):
    if not parsed_uri.path.startswith("/"):
        raise ValueError, "Relative paths are not supported."
    if parsed_uri.netloc:
        raise ValueError, "Netloc in file scheme is unsupported."
    return parsed_uri.path

def package_uri_resolver(parsed_uri):
    return resource_filename(parsed_uri.netloc, parsed_uri.path)

def requirement_uri_resolver(parsed_uri):
    return resource_filename(Requirement.parse(parsed_uri.netloc), parsed_uri.path)

supported_schemes = {
    "file" : file_uri_resolver,
    "" : file_uri_resolver,
    "pkg": package_uri_resolver,
    "req": requirement_uri_resolver,
}

def resource_filename_resolver(resource_uri):
    parsed = urlparse(resource_uri)
    if parsed.scheme not in supported_schemes:
        raise TypeError, "Scheme '%s' is unsupported" % parsed.scheme
    return supported_schemes[parsed.scheme](parsed)
