
from .comment import strip_comment_line_with_symbol, strip_comments  # keep 'unused' imports
from .encoders import TricksEncoder, json_date_time_encode, class_instance_encode, ClassInstanceEncoder  # keep 'unused' imports
from .decoders import DuplicateJsonKeyException, TricksPairHook, json_date_time_hook, ClassInstanceHook, \
	json_complex_hook  # keep 'unused' imports
from .nonp import NoNumpyException, DEFAULT_ENCODERS, _cih_instance
from . import nonp

try:
	from numpy import ndarray, asarray, generic, int64, float64, complex128
	import numpy as nptypes
except ImportError:
	raise NoNumpyException('Could not load numpy, maybe it is not installed? If you do not want to use numpy encoding '
		'or decoding, you can import the functions from json_tricks.nonp instead, which do not need numpy.')


class NumpyTricksEncoder(TricksEncoder):
	def _iterencode(self, o, *args, **kwargs):
		"""
		It is necessary to add a 'hack' here to handle numpy types which overlap with Python
		primitive types. Primitive types are handled without ever reaching custom `.default`,
		so int64, float64 and complex128 can not be encoded without this 'hack'.
		EDIT: this doesn't work recursively, it's not possible...
		"""
		print('ENCODE', o)
		if isinstance(o, (int64, float64, complex128,)):
			print(o, o.dtype)
			o = self.default(obj=o)
		return super(NumpyTricksEncoder, self)._iterencode(o=o, *args, **kwargs)


def numpy_encode(obj):
	# print('numpy_encode')
	if isinstance(obj, ndarray):
		# print('ndarray')
		dct = dict(__ndarray__=obj.tolist(), dtype=str(obj.dtype), shape=obj.shape)
		if len(obj.shape) > 1:
			dct['Corder'] = obj.flags['C_CONTIGUOUS']
		return dct
	elif isinstance(obj, generic):
		# print('generic')
		dct = dict(__ndarray__=obj.item(), dtype=str(obj.dtype), shape=())
		return dct
	# else:
	# 	print('no')
	return obj


class NumpyEncoder(ClassInstanceEncoder):
	"""
	JSON encoder for numpy arrays.
	"""
	def default(self, obj, *args, **kwargs):
		"""
		If input object is a ndarray it will be converted into a dict holding
		data type, shape and the data. The object can be restored using json_numpy_obj_hook.
		"""
		obj = numpy_encode(obj)
		return super(NumpyEncoder, self).default(obj, *args, **kwargs)


def json_numpy_obj_hook(dct):
	"""
	Replace any numpy arrays previously encoded by NumpyEncoder to their proper
	shape, data type and data.

	:param dct: (dict) json encoded ndarray
	:return: (ndarray) if input was an encoded ndarray
	"""
	if isinstance(dct, dict) and '__ndarray__' in dct:
		order = 'A'
		if 'Corder' in dct:
			order = 'C' if dct['Corder'] else 'F'
		if dct['shape']:
			return asarray(dct['__ndarray__'], dtype=dct['dtype'], order=order)
		else:
			# print(dct['dtype'])
			# print(getattr(nptypes, dct['dtype']))
			dtype = getattr(nptypes, dct['dtype'])
			return dtype(dct['__ndarray__'])
			# return asarray(dct['__ndarray__'], dtype=dct['dtype'], order=order)
	return dct


DEFAULT_NP_ENCODERS = (numpy_encode,) + DEFAULT_ENCODERS  # numpy encode needs to be before complex
DEFAULT_NP_HOOKS = (json_numpy_obj_hook, json_date_time_hook, _cih_instance, json_complex_hook,)


def dumps(obj, sort_keys=None, cls=NumpyTricksEncoder, obj_encoders=DEFAULT_NP_ENCODERS,
		extra_obj_encoders=(), compression=None, **jsonkwargs):
	"""
	Just like `nonp.dumps` but with numpy functionality enabled.
	"""
	return nonp.dumps(obj, sort_keys=sort_keys, cls=cls, obj_encoders=obj_encoders,
		extra_obj_encoders=extra_obj_encoders, compression=compression, **jsonkwargs)


def dump(obj, fp, sort_keys=None, cls=NumpyTricksEncoder, obj_encoders=DEFAULT_NP_ENCODERS, extra_obj_encoders=(),
		compression=None, force_flush=False, **jsonkwargs):
	"""
	Just like `nonp.dump` but with numpy functionality enabled.
	"""
	return nonp.dump(obj, fp, sort_keys=sort_keys, cls=cls, obj_encoders=obj_encoders,
		extra_obj_encoders=extra_obj_encoders, compression=compression, force_flush=force_flush, **jsonkwargs)


def loads(string, preserve_order=True, ignore_comments=True, decompression=None, obj_pairs_hooks=DEFAULT_NP_HOOKS,
		extra_obj_pairs_hooks=(), cls_lookup_map=None, allow_duplicates=True, **jsonkwargs):
	"""
	Just like `nonp.loads` but with numpy functionality enabled.
	"""
	return nonp.loads(string, preserve_order=preserve_order, ignore_comments=ignore_comments, decompression=decompression,
		obj_pairs_hooks=obj_pairs_hooks, extra_obj_pairs_hooks=extra_obj_pairs_hooks, cls_lookup_map=cls_lookup_map,
		allow_duplicates=allow_duplicates, **jsonkwargs)


def load(fp, preserve_order=True, ignore_comments=True, decompression=None, obj_pairs_hooks=DEFAULT_NP_HOOKS,
		extra_obj_pairs_hooks=(), cls_lookup_map=None, allow_duplicates=True, **jsonkwargs):
	"""
	Just like `nonp.load` but with numpy functionality enabled.
	"""
	return nonp.load(fp, preserve_order=preserve_order, ignore_comments=ignore_comments, decompression=decompression,
		obj_pairs_hooks=obj_pairs_hooks, extra_obj_pairs_hooks=extra_obj_pairs_hooks, cls_lookup_map=cls_lookup_map,
		allow_duplicates=allow_duplicates, **jsonkwargs)


