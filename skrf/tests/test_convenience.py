
import unittest
import os
import numpy as npy

import skrf as rf


class ConvenienceTestCase(unittest.TestCase):
    '''
    '''
    def setUp(self):
        '''
        '''
        self.test_dir = os.path.dirname(os.path.abspath(__file__))+'/'
        self.hfss_oneport_file = os.path.join(self.test_dir, 'hfss_oneport.s1p')
        self.hfss_twoport_file = os.path.join(self.test_dir, 'hfss_twoport.s2p')
        self.hfss_threeport_file=os.path.join(self.test_dir, 'hfss_threeport_DB.s3p')
        self.hfss_threeport_file_50ohm=os.path.join(self.test_dir, 'hfss_threeport_DB_50Ohm.s3p')
        self.hfss_18dot2 = os.path.join(self.test_dir, 'hfss_18.2.s3p')
        self.hfss_8ports = os.path.join(self.test_dir, 'hfss_19.2.s8p')
        self.hfss_10ports = os.path.join(self.test_dir, 'hfss_19.2.s10p')
        self.ntwk1 = rf.Network(os.path.join(self.test_dir, 'ntwk1.s2p'))
        self.ntwk2 = rf.Network(os.path.join(self.test_dir, 'ntwk2.s2p'))
        self.ntwk3 = rf.Network(os.path.join(self.test_dir, 'ntwk3.s2p'))

    def test_hfss_high_port_number(self):
        '''
        Check dimensions s, gamma and z0 of Network from HFSS .sNp files 
        
        HFSS exports .sNp files with N > 4 with Gamma and Z0 as comments and
        written on multiple lines. The additional lines start with a '!' that 
        need to be escaped to avoid numerical conversion error. 
        '''
        _3ports = rf.Network(self.hfss_18dot2)
        self.assertTrue(_3ports.s.shape[1:] == (3,3))
        self.assertTrue(_3ports.z0.shape[1] == 3)
        self.assertTrue(_3ports.gamma.shape[1] == 3)
        
        _8ports = rf.Network(self.hfss_8ports)
        self.assertTrue(_8ports.s.shape[1:] == (8,8))
        self.assertTrue(_8ports.z0.shape[1] == 8)
        self.assertTrue(_8ports.gamma.shape[1] == 8)

        _10ports = rf.Network(self.hfss_10ports)
        self.assertTrue(_10ports.s.shape[1:] == (10,10))
        self.assertTrue(_10ports.z0.shape[1] == 10)
        self.assertTrue(_10ports.gamma.shape[1] == 10)
        

    def test_hfss_touchstone_2_media(self):
        '''
        currently, this just tests the execution ability. it would
        be better to simulate a uniform line, in hfss and then confirm
        that the hfss network is same as the one generated by the
        media object this function returns
        '''
        med = rf.hfss_touchstone_2_media(self.hfss_oneport_file)[0]
        med.line(1)
        med_p1,med_p2 = rf.hfss_touchstone_2_media(self.hfss_twoport_file)
        med_p1.line(1)
        med_p2.line(1)
        
    def test_hfss_touchstone_renormalization(self):
        '''
        Scattering matrices are given for a given impedance z0, 
        which is usually assumed to be 50 Ohm, unless otherwise stated.
        
        Touchstone files are not necessarly indicating such impedances, 
        especially if they vary with frequency.
        
        HFSS Touchstone file format supports port informations (as an option) for gamma and z0
        When HFSS files are read with Network() (or hfss_touchstone_2_network()),
        the port informations are taken into account.
        '''
        # Comparing the S-params of the same device expressed with same z0 
        nw_50 = rf.Network(self.hfss_threeport_file_50ohm)
        nw = rf.Network(self.hfss_threeport_file)
        nw.renormalize(z_new=50)       
        self.assertTrue(npy.all(npy.abs(nw.s - nw_50.s) < 1e-6))
        
    def test_is_hfss_touchstone(self):
        '''
        Test if Touchstone files have been generated by HFSS or not
        '''
        # Touchstone file generated by HFSS      
        self.assertTrue(rf.Touchstone(self.hfss_oneport_file).is_from_hfss() )
        self.assertTrue(rf.Touchstone(self.hfss_twoport_file).is_from_hfss() )
        self.assertTrue(rf.Touchstone(self.hfss_threeport_file).is_from_hfss() )
        self.assertTrue(rf.Touchstone(self.hfss_18dot2).is_from_hfss())
        self.assertTrue(rf.Touchstone(self.hfss_8ports).is_from_hfss())
        self.assertTrue(rf.Touchstone(self.hfss_10ports).is_from_hfss())
        # Touchstone file not from HFSS       
        self.assertFalse(rf.Touchstone(os.path.join(self.test_dir, 'ntwk1.s2p')).is_from_hfss() )
        
    def test_hfss_touchstone_2_network(self):
        '''
        Test the conversion into a Network of HFSS-generated touchstone files
        '''
        nw_hfss_wo_z0 = rf.Network(os.path.join(self.test_dir, 'hfss_threeport_MA_without_gamma_z0_50Ohm.s3p'))
        nw_hfss_50 = rf.Network(os.path.join(self.test_dir, 'hfss_threeport_MA_50Ohm.s3p'))
        nw_hfss_z0 = rf.Network(os.path.join(self.test_dir, 'hfss_threeport_MA.s3p'))
        # Test if the values read are the same 
        self.assertTrue(npy.allclose(nw_hfss_50.s, nw_hfss_wo_z0.s))
        nw_hfss_z0.renormalize(50)
        self.assertTrue(npy.allclose(nw_hfss_50.s, nw_hfss_z0.s))
        
    def test_cst_touchstone_2_network(self):
        '''
        Test the conversion into a Network of CST-generated touchstone file
        '''
        nw_cst_4ports = rf.Network(os.path.join(self.test_dir, 'cst_example_4ports.s4p'))
        nw_cst_6ports = rf.Network(os.path.join(self.test_dir, 'cst_example_6ports.s6p'))
        
    def test_cst_touchstone_V2_as_V1_2_network(self):
        '''
        Test the conversion into a Network of a CST-generated 
        touchstone V2 format file (.ts) saved like a touchstone V1 file (.sNp)
        '''
        nw_cst_6ports = rf.Network(os.path.join(self.test_dir, 'cst_example_6ports_V2.s6p'))
 
    def test_cst_touchstone_V2_2_network(self):
        '''
        Test the conversion into a Network of a CST-generated touchstone V2 format file (.ts) 
        '''
        nw_cst_6ports = rf.Network(os.path.join(self.test_dir, 'cst_example_6ports_V2.ts'))       
        
    def test_Agilent_touchstone_4ports(self):		
        '''		
        Try reading an Agilent touchstone 4-ports measurement file		
        '''		
        filename = 'Agilent_E5071B.s4p'		
        ntwk = rf.Network(os.path.join(self.test_dir, filename))				          
        # Check if port characteric impedance is correctly parsed        
        self.assertTrue(npy.isclose(npy.unique(ntwk.z0), 75)) 
        
        self.assertTrue(npy.allclose(ntwk.s_db[0][1], # check s2n_mag
                                    [-5.252684e+001, -2.278388e-001, -4.435702e+001, -8.235984e+001]))
        self.assertTrue(npy.allclose(ntwk.s_deg[0][1], # check s2n_deg
                                    [-1.350884e+002, 8.767636e+001,	-1.585657e+002,	7.708928e+001]))
        
    def test_RS_touchstone_4ports(self):		
        '''		
        Try reading an R&S touchstone 4-ports measurement file		
        '''		
        filename = 'RS_ZNB8.s4p'		
        ntwk = rf.Network(os.path.join(self.test_dir, filename))		
        # Check if port characteric impedance is correctly parsed		
        self.assertTrue(npy.isclose(npy.unique(ntwk.z0), 50))		
        # For this specific file, the port#1 min return loss is @55.5MHz		
        self.assertTrue(ntwk.frequency.f[npy.argmin(ntwk.s11.s_mag)], 55.5e6)

        self.assertTrue(npy.allclose(ntwk.s_re[0][2], # check s3n_re
                                    [-9.748145748042028E-6, 5.737806652221101E-6, -7.283138400961303E-1,  -7.202238521877286E-6]))
        self.assertTrue(npy.allclose(ntwk.s_im[0][2], # check s3n_im
                                    [4.457944078457155E-6, 5.341399484369366E-6, -4.531402467395991E-1, 5.667857998796495E-7]))                 
        

if __name__ == "__main__":
    from numpy.testing import run_module_suite
    # Launch all tests
    run_module_suite()            
