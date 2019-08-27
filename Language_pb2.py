# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Language.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='Language.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x0eLanguage.proto\"+\n\x0cLanguageInfo\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x02 \x03(\x0c\"-\n\rLanguageTable\x12\x1c\n\x05infos\x18\x01 \x03(\x0b\x32\r.LanguageInfo*6\n\x0cLanguageType\x12\x06\n\x02\x63h\x10\x00\x12\x06\n\x02\x65n\x10\x01\x12\x06\n\x02zh\x10\x02\x12\x06\n\x02jp\x10\x03\x12\x06\n\x02ko\x10\x04\x42-\n\x14\x63om.hyz.g03.protocol\xaa\x02\x14Google.Protobuf.Gameb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_LANGUAGETYPE = _descriptor.EnumDescriptor(
  name='LanguageType',
  full_name='LanguageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ch', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='en', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='zh', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='jp', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ko', index=4, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=110,
  serialized_end=164,
)
_sym_db.RegisterEnumDescriptor(_LANGUAGETYPE)

LanguageType = enum_type_wrapper.EnumTypeWrapper(_LANGUAGETYPE)
ch = 0
en = 1
zh = 2
jp = 3
ko = 4



_LANGUAGEINFO = _descriptor.Descriptor(
  name='LanguageInfo',
  full_name='LanguageInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='LanguageInfo.id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='LanguageInfo.content', index=1,
      number=2, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=61,
)


_LANGUAGETABLE = _descriptor.Descriptor(
  name='LanguageTable',
  full_name='LanguageTable',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='infos', full_name='LanguageTable.infos', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=63,
  serialized_end=108,
)

_LANGUAGETABLE.fields_by_name['infos'].message_type = _LANGUAGEINFO
DESCRIPTOR.message_types_by_name['LanguageInfo'] = _LANGUAGEINFO
DESCRIPTOR.message_types_by_name['LanguageTable'] = _LANGUAGETABLE
DESCRIPTOR.enum_types_by_name['LanguageType'] = _LANGUAGETYPE

LanguageInfo = _reflection.GeneratedProtocolMessageType('LanguageInfo', (_message.Message,), dict(
  DESCRIPTOR = _LANGUAGEINFO,
  __module__ = 'Language_pb2'
  # @@protoc_insertion_point(class_scope:LanguageInfo)
  ))
_sym_db.RegisterMessage(LanguageInfo)

LanguageTable = _reflection.GeneratedProtocolMessageType('LanguageTable', (_message.Message,), dict(
  DESCRIPTOR = _LANGUAGETABLE,
  __module__ = 'Language_pb2'
  # @@protoc_insertion_point(class_scope:LanguageTable)
  ))
_sym_db.RegisterMessage(LanguageTable)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\024com.hyz.g03.protocol\252\002\024Google.Protobuf.Game'))
# @@protoc_insertion_point(module_scope)
