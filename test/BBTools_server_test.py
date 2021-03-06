# -*- coding: utf-8 -*-
import unittest
import os
import time
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint

from ReadsUtils.ReadsUtilsClient import ReadsUtils

from biokbase.workspace.client import Workspace as workspaceService
from BBTools.BBToolsImpl import BBTools
from BBTools.BBToolsServer import MethodContext
from BBTools.authclient import KBaseAuth as _KBaseAuth


class BBToolsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('BBTools'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'BBTools',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.ws = workspaceService(cls.wsURL)
        cls.serviceImpl = BBTools(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.ws.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.ws

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_BBTools_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

        # call this method to get the WS object info of a Paired End Library (will
    # upload the example data if this is the first time the method is called during tests)
    def getPairedEndLibInfo(self):
        if hasattr(self.__class__, 'pairedEndLibInfo'):
            return self.__class__.pairedEndLibInfo

        # copy the local test file to the shared scratch space so that the ReadsUtils
        # container can see it.
        test_fastq_file_local = 'data/interleaved.fastq'
        test_fastq_file_scratch = os.path.join(self.scratch, os.path.basename(test_fastq_file_local))
        shutil.copy(test_fastq_file_local, test_fastq_file_scratch)

        # call the ReadsUtils libary to upload the test data to KBase
        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        paired_end_ref = ru.upload_reads({'fwd_file': test_fastq_file_scratch,
                                          'sequencing_tech': 'artificial reads',
                                          'interleaved': 1, 'wsname': self.getWsName(),
                                          'name': 'test.pe.reads'})['obj_ref']

        # get the object metadata for the new test dataset
        new_obj_info = self.ws.get_object_info_new({'objects': [{'ref': paired_end_ref}]})
        self.__class__.pairedEndLibInfo = new_obj_info[0]
        return new_obj_info[0]


    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    # @unittest.skip('skip')
    def test_basic_app(self):
        # get the test reads library
        lib_info = self.getPairedEndLibInfo()
        print(lib_info)

        io_params = {
            'read_library_ref': str(lib_info[6]) + '/' + str(lib_info[0]) + '/' + str(lib_info[4]),
            'output_workspace_name': self.getWsName(),
            'output_library_name': 'filtered.reads'
        }
        run_params = {}
        bbtools = self.getImpl()
        res = bbtools.run_RQCFilter_app(self.ctx, io_params, run_params)

        print('result:')
        pprint(res)

    def test_app_jgi_parameters(self):
        lib_info = self.getPairedEndLibInfo()
        io_params = {
            'read_library_ref': "{}/{}/{}".format(lib_info[6], lib_info[0], lib_info[4]),
            'output_workspace_name': self.getWsName(),
            'output_library_name': 'filtered_reads_all_params'
        }
        run_params = {
            'rna': 0,
            'trimfragadapter': 1,
            'qtrim': 'r',
            'trimq': 0,
            'maxns': 3,
            'minavgquality': 3,
            'minlength': 51,
            'mlf': 0.333,
            'phix': 1,
            'removehuman': 1,
            'removedog': 1,
            'removecat': 1,
            'removemouse': 1,
            'khist': 1,
            'removemicrobes': 1,
            'clumpify': 1
        }
        bbtools = self.getImpl()
        res = bbtools.run_RQCFilter_app(self.ctx, io_params, run_params)[0]
        print('result:')
        pprint(res)
        self.assertIn('report_name', res)
        self.assertIn('report_ref', res)
        self.assertIn('run_command', res)
        self.assertIn('rqcfilter2.sh', run_command)

    def test_app_bad_parameters(self):
        pass

    def test_app_missing_parameters(self):
        pass

    def test_local_mem_req(self):
        lib_info = self.getPairedEndLibInfo()
        io_params = {
            "read_library_ref": "{}/{}/{}".format(lib_info[6], lib_info[0], lib_info[4]),
        }
        bbtools = self.getImpl()
        res = bbtools.run_RQCFilter_local(self.ctx, io_params, { "maxmem": 5 })
        self.assertIn('output_directory', res)
        self.assertIn('filtered_fastq_file', res)
        self.assertIn('run_log', res)
        self.assertIn('run_command', res)
        self.assertIn('rqcfilter2.sh', res['run_command'])
        self.assertIn('-Xmx5g', res['run_command'])

    def test_local_bad_mem_param(self):
        lib_info = self.getPairedEndLibInfo()
        io_params = {
            "read_library_ref": "{}/{}/{}".format(lib_info[6], lib_info[0], lib_info[4]),
        }
        bbtools = self.getImpl()
        with self.assertRaises(ValueError) as e:
            bbtools.run_RQCFilter_local(self.ctx, io_params, { "maxmem": -1 })
        self.assertIn("The value of maxmem must be an integer > 0.", str(e.exception))
        with self.assertRaises(ValueError) as e:
            bbtools.run_RQCFilter_local(self.ctx, io_params, { "maxmem": "one" })
        self.assertIn("The value of maxmem must be an integer > 0.", str(e.exception))
        with self.assertRaises(ValueError) as e:
            bbtools.run_RQCFilter_local(self.ctx, io_params, { "maxmem": 0 })
        self.assertIn("The value of maxmem must be an integer > 0.", str(e.exception))

    def test_run_local_reads_upa(self):
        lib_info = self.getPairedEndLibInfo()
        print(lib_info)

        io_params = {
            "read_library_ref": "{}/{}/{}".format(lib_info[6], lib_info[0], lib_info[4]),
        }
        run_params = {}
        bbtools = self.getImpl()
        res = bbtools.run_RQCFilter_local(self.ctx, io_params, run_params)[0]
        print('result:')
        pprint(res)
        self.assertIn('output_directory', res)
        self.assertTrue(os.path.exists(res['output_directory']))
        self.assertIn('filtered_fastq_file', res)
        self.assertTrue(os.path.exists(res['filtered_fastq_file']))
        self.assertIn('run_log', res)
        self.assertTrue(os.path.exists(res['run_log']))
        self.assertIn('run_command', res)
        self.assertIn('rqcfilter2.sh', run_command)

    def test_run_local_reads_file(self):
        test_fastq_file_local = os.path.join('data', 'interleaved.fastq')
        test_fastq_file_scratch = os.path.join(self.scratch, os.path.basename(test_fastq_file_local))
        shutil.copy(test_fastq_file_local, test_fastq_file_scratch)

        io_params = {
            "reads_file": test_fastq_file_scratch
        }
        run_params = {}
        bbtools = self.getImpl()
        res = bbtools.run_RQCFilter_local(self.ctx, io_params, run_params)[0]
        print('result:')
        pprint(res)
        self.assertIn('output_directory', res)
        self.assertTrue(os.path.exists(res['output_directory']))
        self.assertIn('filtered_fastq_file', res)
        self.assertTrue(os.path.exists(res['filtered_fastq_file']))
        self.assertIn('run_log', res)
        self.assertTrue(os.path.exists(res['run_log']))
        self.assertIn('run_command', res)
        self.assertIn('rqcfilter2.sh', run_command)


    def test_get_version(self):
        version = self.getImpl().bbtools_version(self.ctx)[0]
        ver_file = "/kb/module/bbmap_version"
        with open(ver_file) as f:
            version_from_file = f.read().strip()
        self.assertEqual(version, version_from_file)