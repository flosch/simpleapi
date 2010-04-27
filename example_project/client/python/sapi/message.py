#This is common between the client & server
__all__ = ['MessageElement', 'Message', 'BaseMessage']

import string, sys, re, json
from xml.etree import cElementTree as ET

def _validate_element(el):
    if not isinstance(el, MessageElement):
        raise TypeError("element must be a MessageElement")

class BaseMessage(dict):
    pass

class MessageElement(BaseMessage):
    """
    MessageElement class. This is used for all items to be sent across
    the network and is wrapped in a Message before being sent across
    So you should only ever be working with this class directly

    @public attributes
        tag
            The primary identifier for the element.
        text
            Any text contents of this message
        children
            Is a readonly list of the children of this element
            Though this is a list modifying it directly to it will
            have no effect on the actual children
        parent
            Is a readonly attribute that holds the parent of this element
            If you append this element to another the parent is reset
        root
            Is a readonly attribute containing the root element that this
            element belongs to. If this is the root element it will return
            itself
    """
    _tag = None
    _text = None
    _parent = None
    _root = None
    _children = None

    def __init__(self, tag, text=None, **kwargs):
        """
        Generate the MessageElement

        @param tag Is the elements tag, which is the primary identifier
        @param text The text contents of this element
        @param **kwargs Is a key, value set of attributes for this element

        @usage;
            MessageElement('example')
            MessageElement('example', 'some text contents')
            MessageElement('example', 'some text contents', attr1=1, ...)
        """
        super(MessageElement, self).__init__(**kwargs)
        self.tag = tag
        self._root = self
        self._children = list()
        if text:
            self.text = text

    def __repr__(self):
        return "<MessageElement(%(tag)s) at 0x%(id)x}>" % {'tag': self.tag,
                                                           'id' : id(self)}

    def __len__(self):
        """
        Returns the number of children

        @return the number of children
        """
        return len(self._children)

    def __getattr__(self, attr):
        """
        Gets an element attribute.

        @return The attribute value, or None
        """
        return self.get(attr, None)

    def __setattr__(self, attr, value):
        """
        Sets an element attribute.
        """
        if attr not in ['_tag', 'tag', '_text', 'text', '_parent', 'parent',
                 '_root', 'root', '_children', 'children']:
            super(MessageElement, self).__setitem__(attr, value)
        else:
            super(MessageElement, self).__setattr__(attr, value)

    def __getitem__(self, index):
        """
        Returns the given subelement.

        @param index What subelement to return.
        @return The given subelement.
        @exception IndexError If the given element does not exist.
        """
        return self._children[index]

    def __setitem__(self, index, element):
        """
        Replaces the given subelement.

        @param index What subelement to replace.
        @param element The new element value.
        @exception IndexError If the given element does not exist.
        @exception TypeError If element is not a valid object.
        """
        _validate_element(element)
        element._adjust_parent_root(self, self.root)
        self._children[index] = element

    def __delitem__(self, index):
        """
        Deletes the given subelement.

        @param index What subelement to delete.
        @exception IndexError If the given element does not exist.
        """
        del self._children[index]

    def __getslice__(self, start, stop):
        """
        Returns a list containing subelements in the given range.

        @param start The first subelement to return.
        @param stop The first subelement that shouldn't be returned.
        @return A sequence object containing subelements.
        """
        return self._children[start:stop]

    def __setslice__(self, start, stop, elements):
        """
        Replaces a number of subelements with elements from a sequence.

        @param start The first subelement to replace.
        @param stop The first subelement that shouldn't be replaced.
        @param elements A sequence object with zero or more elements.
        @exception TypeError If a sequence member is not a valid object.
        """
        for element in elements:
            _validate_element(element)
            element._adjust_parent_root(self, self.root)
        self._children[start:stop] = list(elements)

    def __delslice__(self, start, stop):
        """
        Deletes a number of subelements.

        @param start The first subelement to delete.
        @param stop The first subelement to leave in there.
        """
        del self._children[start:stop]

    def _adjust_parent_root(self, parent, root):
        self._parent = parent
        self._root = root
        for child in self._children:
            child._adjust_parent_root(self, root)

    def to_json(self, as_dict=True):
        _ = {u'tag': self.tag,
             u'attrs': dict(self.iteritems()),
             u'text': self.text,
             u'children': [child.to_json() for child in self._children]}

        if as_dict:
            return _

        return json.dumps(_, ensure_ascii=False)

    def to_xml(self):
        e = ET.Element(self.tag)
        e.text = self.text

        for attr, value in self.iteritems():
            if not isinstance(value, basestring):
                value = str(value)
            e.set(attr, value)

        for child in self._children:
            child_el = child.to_xml()
            e.append(child_el)

        return e

    def append(self, element):
        """
        Adds a subelement to the end of this element.

        @param element The element to add.
        @exception TypeError If the element is not a valid object.
        """
        _validate_element(element)
        element._adjust_parent_root(self, self.root)
        self._children.append(element)

    def insert(self, index, element):
        """
        Inserts a subelement at the given position in this element.

        @param index Where to insert the new subelement.
        @exception TypeError If the element is not a valid object.
        """
        _validate_element(element)
        element._adjust_parent_root(self, self.root)
        self._children.insert(index, element)

    def remove(self, element):
        """
        Removes a matching subelement.  Unlike the <b>find</b> methods,
        this method compares elements based on identity, not on tag
        value or contents.

        @param element What element to remove.
        @exception ValueError If a matching element could not be found.
        @exception TypeError If the element is not a valid object.
        """
        _validate_element(element)
        element._adjust_parent_root(None, element)
        self._children.remove(element)

    def clear(self):
        """
        Resets an element.  This function removes all subelements, clears
        all attributes, and sets the text attribute to None.
        """
        super(MessageElement, self).clear()
        self._children = []
        self.text = None

    def set(self, key, value):
        """
        Sets an element attribute.

        @param key What attribute to set.
        @param value The attribute value.
        """
        self.__setattr__(key, value)

    def find(self, tag):
        """
        Finds the first matching subelement, by tag name.

        @param tag What element to look for.
        @return The first matching element, or None if no element was found.
        @defreturn MessageElement or None
        """
        for child in self._children:
            if child.tag == tag:
                return child

        return None

    def iter_find(self, tag):
        """
        Finds the first matching subelement, by tag name.
        Does so recursivly

        @param tag What element to look for.
        @return The first matching element, or None if no element was found.
        @defreturn MessageElement or None
        """
        for child in self._children:
            if child.tag == tag:
                return child
            check = child.iterfind(tag)
            if check is not None:
                return check

        return None

    def findtext(self, tag, default=""):
        """
        Finds text for the first matching subelement, by tag name.

        @param tag What element to look for.
        @param default What to return if the element was not found.
        @return The text content of the first matching element, or the
            default value no element was found.  Note that if the element
            has is found, but has no text content, this method returns an
            empty string.
        @defreturn string
        """
        el = self.find(tag)
        if el is not None:
            if not el.text:
                return default
            return el.text

        return None

    def iter_findtext(self, tag, default=""):
        """
        Finds text for the first matching subelement, by tag name.
        Does so recursivly

        @param tag What element to look for.
        @param default What to return if the element was not found.
        @return The text content of the first matching element, or the
            default value no element was found.  Note that if the element
            has is found, but has no text content, this method returns an
            empty string.
        @defreturn string
        """
        el = self.iterfind(tag)
        if el is not None:
            if not el.text:
                return default
            return el.text

        return None

    def findall(self, tag):
        """
        Finds all matching elements, by tag name.

        @param tag What element to look for.
        @return A list or iterator containing all matching elements,
           in document order.
        @defreturn list of Element instances
        """
        found = []
        for child in self.children:
            if child.tag == tag:
                found.append(child)
            found.extend(child.findall(tag))
        return found

    def getiterator(self, tag=None):
        """
        Creates a tree iterator.  The iterator loops over this element
        and all subelements, in document order, and returns all elements
        with a matching tag.

        If the tree structure is modified during iteration, the result
        is undefined.

        @param tag What tags to look for (default is to return all elements).
        @return A list or iterator containing all the matching elements.
        @defreturn list or iterator
        """
        if tag == "*" or tag is None or self.tag == tag:
            yield self

        for node in self._children:
            for item in node.getiterator(tag):
                yield item

    @classmethod
    def parse_json(cls, source):
        """
        Parse the source and turn it into a proper MessageElement

        @param source A string or dict
        @return The MessageElement
        @defreturn MessageElement
        """
        if isinstance(source, basestring):
            source = json.loads(source, encoding='utf-8')

        el = cls(source['tag'], **source.get('attrs', {}))
        if source.get('text'):
            el.text = source['text']

        for child in source.get('children', []):
            el.append(cls.parse_json(child))

        return el

    @classmethod
    def parse_xml(cls, source):
        """
        Parses a xml String into a MessageElement

        @param source A json string.
        @return The MessageElement.
        @defreturn MessageElement
        """
        if isinstance(source, basestring):
            source = ET.fromstring(source)

        el = cls(source.tag, **source.attrib)
        if source.text:
            el.text = source.text

        children = source.getchildren()
        for child in children:
            el.append(cls.parse_xml(child))

        return el

    #Properties
    def _get_tag(self):
        return self._tag
    def _set_tag(self, value):
        if not isinstance(value, basestring):
            raise TypeError("tag must be a string")

        self._tag = value
    tag = property(_get_tag, _set_tag, doc="The MessageElement tag")

    def _get_text(self):
        return self._text
    def _set_text(self, value):
        if not isinstance(value, basestring):
            raise TypeError("text must be a string")

        self._text = value
    def _del_text(self):
        self._text = None
    text = property(_get_text, _set_text, _del_text,
                    doc="The MessageElement text")

    def _get_children(self):
        if self._children is None:
            self._children = []
        return list(self._children)
    children = property(_get_children, None, doc="The MessageElements children")

    def _get_parent(self):
        return self._parent
    def _del_parent(self):
        self._parent = None
    parent = property(_get_parent, None, _del_parent,
                      doc="The MessageElements parent")

    def _get_root(self):
        return self._root
    def _del_root(self):
        self._root = self
    root = property(_get_root, None, _del_root,
                    doc="The MessageElements root")

class Message(BaseMessage):
    """
    Message wrapper class.  This class represents an entire message
    hierarchy, and adds some extra support for serialization to and from
    standard json.

    @param element Optional root element.
    """
    _root = None
    _errors = None
    _text = None

    def __init__(self, element=None, **kwargs):
        super(Message, self).__init__(**kwargs)

        self._errors = list()

        if element is not None:
            _validate_element(element)
            self._root = element

    def __getattr__(self, attr):
        """
        Gets an element attribute.

        @return The attribute value, or None
        """
        return self.get(attr, None)

    def __setattr__(self, attr, value):
        """
        Sets an element attribute.
        """
        if attr not in ['_text', 'text', '_root', 'root', '_errors', 'errors']:
            super(Message, self).__setitem__(attr, value)
        else:
            super(Message, self).__setattr__(attr, value)

    def __repr__(self):
        return '<Message at 0x%x>' % id(self)


    def to_json(self, as_dict=True):
        _ = {u'simpleapi': 'response',
             u'error': True if self._errors else False,
             u'errors': tuple(self.errors),
             u'attrs': dict(self.iteritems()),
             u'text': self.text,
             u'root': self.root.to_json() if self.root else None}

        if as_dict:
            return _

        return json.dumps(_, ensure_ascii=False)

    def to_xml(self):
        e = ET.Element('response')
        for attr, value in self.iteritems():
            if not isinstance(value, basestring):
                value = str(value)
            e.set(attr, value)
        e.text = self._text

        if self.errors:
            errs = ET.Element('errors')
            for error in self.errors:
                err = ET.Element('error')
                err.text = error
                errs.append(err)
            e.append(errs)

        if self._root:
            root_el = self._root.to_xml()
            e.append(root_el)

        return ET.tostring(e)

    def clear(self):
        """
        Resets an element.  This function removes all subelements, clears
        all attributes, and sets the text attribute to None.
        """
        super(Message, self).clear()
        self._errors = list()
        self.text = None
        self._root = None

    def get(self, attr, default=None):
        if attr == 'result':
            return self
        elif attr == 'errors':
            return self.errors

        return super(Message, self).get(attr, default)

    def set(self, key, value):
        """
        Sets an element attribute.

        @param key What attribute to set.
        @param value The attribute value.
        """
        self.__setattr__(key, value)

    def add_error(self, message):
        self._errors.append(message)

    def getiterator(self, tag=None):
        """
        Creates a tree iterator for the root element.  The iterator loops
        over all elements in this tree, in document order.

        @param tag What tags to look for (default is to return all elements)
        @return An iterator.
        @defreturn iterator
        """
        if self._root is not None:
            for item in self._root.getiterator(tag):
                yield item

    def find(self, tag):
        """
        Finds the first toplevel element with given tag.
        Same as root.find(tag).

        @param tag What element to look for.
        @return The first matching element, or None if no element was found.
        @defreturn MessageElement or None
        """
        if self._root is None:
            return

        return self._root.find(tag)

    def iter_find(self, tag):
        """
        Finds the first toplevel element with given tag.
        Same as getroot().find(tag).

        @param tag What element to look for.
        @return The first matching element, or None if no element was found.
        @defreturn MessageElement or None
        """
        if self._root is None:
            return

        return self._root.iter_find(tag)

    def findtext(self, tag, default=None):
        """
        Finds the element text for the first toplevel element with given
        tag.  Same as root.findtext(tag).

        @param tag What toplevel element to look for.
        @param default What to return if the element was not found.
        @return The text content of the first matching element, or the
            default value no element was found.  Note that if the element
            has is found, but has no text content, this method returns an
            empty string.
        @defreturn string
        """
        if self._root is None:
            return

        return self._root.findtext(tag, default)

    def iter_findtext(self, tag, default=None):
        """
        Finds the element text for the first toplevel element with given
        tag.  Same as root.findtext(tag).

        @param tag What toplevel element to look for.
        @param default What to return if the element was not found.
        @return The text content of the first matching element, or the
            default value no element was found.  Note that if the element
            has is found, but has no text content, this method returns an
            empty string.
        @defreturn string
        """
        if self._root is None:
            return

        return self._root.iter_findtext(tag, default)

    def findall(self, tag):
        """
        Finds all toplevel elements with the given tag.
        Same as root.findall(tag).

        @param tag What element to look for.
        @return A list or iterator containing all matching elements,
           in document order.
        @defreturn list of MessageElement instances
        """
        if self._root is None:
            return []

        return self._root.findall(tag)

    @classmethod
    def parse_json(cls, source):
        """
        Parses a json String into a Message

        @param source A json string.
        @return The Message.
        @defreturn Message
        """
        if isinstance(source, basestring):
            source = json.loads(source, encoding='utf-8')

        if source.get('root'):
            ret = cls(MessageElement.parse_json(source['root']),
                      **source.get('attrs', {}))
        else:
            ret = cls(**source.get('attrs', {}))

        if source.get('text'):
            ret.text = source['text']

        for error in source.get('errors', []):
            ret.add_error(error)

        for attr, value in source.get('attrs', {}).iteritems():
            ret.set(attr, value)

        return ret

    @classmethod
    def parse_xml(cls, source):
        """
        Parses a xml String into a Message

        @param source A json string.
        @return The Message.
        @defreturn Message
        """
        if isinstance(source, basestring):
            source = ET.fromstring(source)

        if source.tag != 'response':
            raise TypeError('Message does not know how to decode this')

        ret = cls()

        for attr, value in source.attrib.iteritems():
            ret.set(attr, value)

        for err in source.findall('error'):
            ret.add_error(err.text)
            source.remove(err)

        for errs in source.findall('errors'):
            source.remove(errs)

        children = source.getchildren()
        child = children[0] if len(children) else None
        if child is not None:
            c = MessageElement.parse_xml(child)
            ret._root = c

        return ret

    #Properties
    def _get_root(self):
        return self._root
    root = property(_get_root, None, doc="The root MessageElement or None")

    def _get_text(self):
        return self._text
    def _set_text(self, value):
        if not isinstance(value, basestring):
            raise TypeError("text must be a string")

        self._text = value
    def _del_text(self):
        self._text = None
    text = property(_get_text, _set_text, _del_text,
                    doc="The text contents of this message")

    def _get_errors(self):
        if self._errors is None:
            self._errors = list()
        return list(self._errors)
    errors = property(_get_errors)

    def _get_has_errors(self):
        return True if self._errors else False
    has_errors = property(_get_has_errors)
