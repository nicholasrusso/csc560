from os import environ
from distutils.core import setup, Extension

if 'PYTHON_35_INCLUDE' in environ:
    print('Found PYTHON_35_INCLUDE env var:', environ['PYTHON_35_INCLUDE'])
    python35Include = environ['PYTHON_35_INCLUDE']
else:
    print('''Couldn\'t find PYTHON_35_INCLUDE environment var.
        Please set PYTHON_35_INCLUDE to your Python3.5 include directory.
        You may be able to locate the directory with "locate Python.h"''')
    exit()

if 'PYTHON_35_LIB' in environ:
    print('Found PYTHON_35_LIB env var:', environ['PYTHON_35_LIB'])
    python35Lib = environ['PYTHON_35_LIB']
else:
    print('''Couldn\'t find PYTHON_35_LIB environment var.
        Please set PYTHON_35_LIB to your Python 3.5 library location.
        Likely located under /usr/lib/python3.5''')
    exit()

if 'POSTGRES_LIB' in environ:
    print('Found POSTGRES_LIB environment var:', environ['POSTGRES_LIB'])
    postgresLib = environ['POSTGRES_LIB']
else:
    print('''Couldn't find POSTGRES_LIB environment var.
        Please set POSTGRES_LIB to your Postgres installation's lib directory.
        If installed from source, the default location is /usr/local/pgsql/lib''')
    exit()

pgParseModule = Extension('mypgparse',
                          extra_compile_args=['-Wall',
                                              '-Wno-unused-function',
                                              '-Wno-unused-value',
                                              '-Wno-unused-variable',
                                              '-fno-strict-aliasing',
                                              '-fwrapv',
                                              '-fPIC',
                                              '-L/lib64',
                                              '-lpthread'],
                          include_dirs=[python35Include,
                                        '.',
                                        'src',
                                        'src/postgres/include'],
                          libraries=['m',
                                     'rt',
                                     'dl'],
                          library_dirs=[python35Lib,
                                        postgresLib],
                          sources=['src/pythonInterface.c'],
                          extra_objects=[
                              'src/pg_query_fingerprint.o',
                              'src/pg_query_json.o',
                              'src/pg_query_json_plpgsql.o',
                              'src/pg_query_normalize.o',
                              'src/pg_query.o',
                              'src/pg_query_parse.o',
                              'src/pg_query_parse_plpgsql.o',
                              'src/postgres/contrib_pgcrypto_sha1.o',
                              'src/postgres/src_backend_catalog_namespace.o',
                              'src/postgres/src_backend_catalog_pg_proc.o',
                              'src/postgres/src_backend_commands_define.o',
                              'src/postgres/src_backend_libpq_pqcomm.o',
                              'src/postgres/src_backend_lib_stringinfo.o',
                              'src/postgres/src_backend_nodes_bitmapset.o',
                              'src/postgres/src_backend_nodes_copyfuncs.o',
                              'src/postgres/src_backend_nodes_equalfuncs.o',
                              'src/postgres/src_backend_nodes_list.o',
                              'src/postgres/src_backend_nodes_makefuncs.o',
                              'src/postgres/src_backend_nodes_nodeFuncs.o',
                              'src/postgres/src_backend_nodes_value.o',
                              'src/postgres/src_backend_parser_gram.o',
                              'src/postgres/src_backend_parser_keywords.o',
                              'src/postgres/src_backend_parser_kwlookup.o',
                              'src/postgres/src_backend_parser_parse_expr.o',
                              'src/postgres/src_backend_parser_parser.o',
                              'src/postgres/src_backend_parser_scan.o',
                              'src/postgres/src_backend_parser_scansup.o',
                              'src/postgres/src_backend_postmaster_postmaster.o',
                              'src/postgres/src_backend_storage_ipc_ipc.o',
                              'src/postgres/src_backend_tcop_postgres.o',
                              'src/postgres/src_backend_utils_adt_datum.o',
                              'src/postgres/src_backend_utils_adt_expandeddatum.o',
                              'src/postgres/src_backend_utils_adt_format_type.o',
                              'src/postgres/src_backend_utils_adt_ruleutils.o',
                              'src/postgres/src_backend_utils_error_assert.o',
                              'src/postgres/src_backend_utils_error_elog.o',
                              'src/postgres/src_backend_utils_init_globals.o',
                              'src/postgres/src_backend_utils_mb_encnames.o',
                              'src/postgres/src_backend_utils_mb_mbutils.o',
                              'src/postgres/src_backend_utils_mb_wchar.o',
                              'src/postgres/src_backend_utils_misc_guc.o',
                              'src/postgres/src_backend_utils_mmgr_aset.o',
                              'src/postgres/src_backend_utils_mmgr_mcxt.o',
                              'src/postgres/src_common_psprintf.o',
                              'src/postgres/src_pl_plpgsql_src_pl_comp.o',
                              'src/postgres/src_pl_plpgsql_src_pl_funcs.o',
                              'src/postgres/src_pl_plpgsql_src_pl_gram.o',
                              'src/postgres/src_pl_plpgsql_src_pl_handler.o',
                              'src/postgres/src_pl_plpgsql_src_pl_scanner.o',
                              'src/postgres/src_port_qsort.o'
                          ])

setup(name='mypgparse',
      version='1.0',
      description='Create query trees using the PostgreSQL parser',
      author='Brandon Cooper',
      ext_modules=[pgParseModule])
