# -*- coding: utf-8 -*-

"""
Definition of nodes for plotting graphs with igraph package
"""

import numpy as np
import os

from nipype.interfaces.base import BaseInterface, \
    BaseInterfaceInputSpec, traits, File, TraitedSpec, isdefined

#import nibabel as nib
#from nipype.utils.filemanip import split_filename as split_f
    
         
######################################################################################## PlotIGraphModules ##################################################################################################################

from graphpype.utils_net import read_lol_file,read_Pajek_corres_nodes_and_sparse_matrix
from graphpype.plot_igraph import plot_3D_igraph_all_modules,plot_3D_igraph_single_modules

import csv

class PlotIGraphModulesInputSpec(BaseInterfaceInputSpec):
    
    rada_lol_file = File(exists=True, desc="modularity structure description, generated by radatools", mandatory=True)
    Pajek_net_file = File(exists=True, desc='net description in Pajek format', mandatory=True)
    coords_file = File(exists=True, desc="txt file containing the coords of the nodes", mandatory=False)
    labels_file = File(exists=True, desc="txt file containing the labels of the nodes (full description)", mandatory=False)
    node_roles_file = File(exists=True, desc="txt file containing the roles of the nodes (integer labels)", mandatory=False)
    
class PlotIGraphModulesOutputSpec(TraitedSpec):
    
    #Z_list_single_modules_files = traits.List(File(exists=True), desc="graphical representation in space of each module independantly")    
    all_modules_files = traits.List(File(exists=True), desc="graphical representation in space (possibly, if coords is given) from different point of view of all modules together + (surely) topological representation")
    
class PlotIGraphModules(BaseInterface):
    
    """
    Description:
    
    Graphical representation of the modular structure of the network. 
    If coords are provided, plot in space, otherwise use topological space.    
    If node labels are provided, write them on the graph
    In node roles are provided , node shape are diplayed on the graph
    
    Inputs:
        
        rada_lol_file: 
            type = File, exists=True, desc="modularity structure description, generated by radatools", mandatory=True
            
        Pajek_net_file:
            type = File, exists=True, desc='net description in Pajek format', mandatory=True
            
        coords_file:
            type = File, exists=True, desc="txt file containing the coords of the nodes", mandatory=False
            
        labels_file: 
            type = File, exists=True, desc="txt file containing the labels of the nodes (full description)", mandatory=False
            
        node_roles_file:
            type = File, exists=True, desc="txt file containing the roles of the nodes (integer labels)", mandatory=False
    
    Outputs:
          
        all_modules_files: 
            type = List of Files, (exists=True), desc="graphical representation in space (possibly, if coords is given) from different point of view of all modules together + (surely) topological representation"
    
        
    """
    
    
    input_spec = PlotIGraphModulesInputSpec
    output_spec = PlotIGraphModulesOutputSpec

    
    def _run_interface(self, runtime):
                
                
        rada_lol_file = self.inputs.rada_lol_file
        Pajek_net_file = self.inputs.Pajek_net_file
        coords_file = self.inputs.coords_file
        labels_file = self.inputs.labels_file
        node_roles_file = self.inputs.node_roles_file
        
        print('Loading node_corres and Z list')
        
        node_corres,Z_list = read_Pajek_corres_nodes_and_sparse_matrix(Pajek_net_file)
        
        print(np.min(node_corres),np.max(node_corres))
        
        print(node_corres.shape)
        print(node_corres)
        
        print(Z_list)
        print(Z_list.shape) 
        
        print('Loading coords')
        
        #print 'Loading gm mask coords'
        
        #gm_mask_coords = np.array(np.loadtxt(gm_mask_coords_file),dtype = 'int64')
        
        #print gm_mask_coords.shape
        
        print("Loading community belonging file" + rada_lol_file)

        community_vect = read_lol_file(rada_lol_file)
        
        print(community_vect)
        print(community_vect.shape)
        print(np.min(community_vect),np.max(community_vect))
        
        if isdefined(coords_file):
            
            print('extracting node coords')
            
            coords = np.array(np.loadtxt(coords_file),dtype = 'float')
            print(coords.shape)
            
            node_coords = coords[node_corres,:]
            print(node_coords.shape)
            
            #print np.isnan(node_coords)
            
            #node_coords[np.isnan(node_coords)] = -100
            ##print node_coords
                        
        else :
            node_coords = np.array([])
            
            
        if isdefined(labels_file):
            
            print('extracting node labels')
                   
            labels = [line.strip() for line in open(labels_file)]
            print(labels)
            
            node_labels = np.array(labels,dtype = 'string')[node_corres].tolist()
            print(len(node_labels))
            
        else :
            node_labels = node_corres.tolist()
            
        if isdefined(node_roles_file):
        
            print('extracting node roles')
                    
            node_roles = np.array(np.loadtxt(node_roles_file),dtype = 'int64')
            
            #print node_roles 
            
        else:
        
            node_roles = np.array([])
           
            
        #print node_roles 
        
        print("plotting 3D modules with igraph")
        
        #Z_list_single_modules_files = plot_3D_igraph_single_modules(community_vect,Z_list,node_coords,node_labels,node_roles = node_roles,nb_min_nodes_by_module = 5)
        
        print(node_coords.size)
        
        if node_coords.size != 0:
        
            self.all_modules_files = plot_3D_igraph_all_modules(community_vect,Z_list,node_coords,node_labels,node_roles = node_roles)
        else:
            self.all_modules_files = []
           
        FR_module_file = plot_3D_igraph_all_modules(community_vect,Z_list,node_labels= node_labels,node_roles = node_roles, layout = 'FR')
        
        self.all_modules_files.append(FR_module_file)
        
        return runtime
        
    def _list_outputs(self):
        
        outputs = self._outputs().get()
        
        outputs["all_modules_files"] =self.all_modules_files 
        
        
        return outputs

############################################################################################### PlotIGraphCoclass #####################################################################################################

from nipype.utils.filemanip import split_filename as split_f

from graphpype.plot_igraph import plot_3D_igraph_bin_mat
    
class PlotIGraphCoclassInputSpec(BaseInterfaceInputSpec):
    
    coclass_matrix_file = File(exists=True,  desc='coclass matrix in npy format', mandatory=True)
    
    labels_file = File(exists=True,  desc='labels of nodes', mandatory=False)
    
    threshold = traits.Int(50, usedefault = True, desc='What min coclass value is reresented by an edge on the graph', mandatory=False)
    
    gm_mask_coords_file = File(exists=True,  desc='node coordinates in MNI space (txt file)', mandatory=False)
    
class PlotIGraphCoclassOutputSpec(TraitedSpec):
    
    plot_igraph_3D_coclass_matrix_file = File(exists=True, desc="eps file with igraph graphical representation")
    
class PlotIGraphCoclass(BaseInterface):
    
    """
    Description
    
    Plot coclassification matrix with igraph
    - labels are optional, 
    - threshold is optional (default, 50 = half the group)
    - coordinates are optional, if no coordinates are specified, representation in topological (Fruchterman-Reingold) space
    
    Inputs:
        
        coclass_matrix_file:
            type = File, exists=True,  desc='coclass matrix in npy format', mandatory=True
        
        labels_file:
            type = File, exists=True,  desc='labels of nodes', mandatory=False
        
        threshold:
            type = Int,default = 50, usedefault = True, desc='What min coclass value is reresented by an edge on the graph', mandatory=False
        
        gm_mask_coords_file:
            type = File, exists=True,  desc='node coordinates in MNI space (txt file)', mandatory=False
        
    Outputs:
        
        plot_igraph_3D_coclass_matrix_file:
            type = File, exists=True, desc="eps file with igraph graphical representation"
    
    Comments:
    
    Used for coclassification, not so much used anymore
    
    """
    input_spec = PlotIGraphCoclassInputSpec
    output_spec = PlotIGraphCoclassOutputSpec

    def _run_interface(self, runtime):
                
        print('in plot_coclass')
        
        coclass_matrix_file = self.inputs.coclass_matrix_file
        labels_file = self.inputs.labels_file
        
        threshold = self.inputs.threshold
        gm_mask_coords_file = self.inputs.gm_mask_coords_file
        
        
        print('loading coclass')
        coclass_matrix = np.load(coclass_matrix_file)
        
        
        if isdefined(labels_file):
            
            print('loading labels')
            labels = [line.strip() for line in open(labels_file)]
            
        else :
            labels = []
            
        if isdefined(gm_mask_coords_file):
            
            print('loading coords')
            
            gm_mask_coords = np.loadtxt(gm_mask_coords_file)
            
        else :
            gm_mask_coords = np.array([])
            
            
        print('thresholding coclass')
        
        coclass_matrix[coclass_matrix <= threshold] = 0
        
        coclass_matrix[coclass_matrix > threshold] = 1
        
        print(coclass_matrix)
        
        print('plotting igraph')
        
        
        plot_igraph_3D_coclass_matrix_file = os.path.abspath("plot_3D_signif_coclass_mat.eps")
        
        plot_3D_igraph_bin_mat(plot_igraph_3D_coclass_matrix_file,coclass_matrix,coords = gm_mask_coords,labels = labels)
        
        return runtime
        
    def _list_outputs(self):
        
        outputs = self._outputs().get()
        
        outputs["plot_igraph_3D_coclass_matrix_file"] = os.path.abspath("plot_3D_signif_coclass_mat.eps")
        
        return outputs
        
        
############################################################################################### PlotIGraphConjCoclass #####################################################################################################

from graphpype.plot_igraph import plot_3D_igraph_int_mat
from graphpype.utils import check_np_shapes

class PlotIGraphConjCoclassInputSpec(BaseInterfaceInputSpec):
    
    coclass_matrix_file1 = File(exists=True,  desc='coclass matrix in npy format', mandatory=True)
    coclass_matrix_file2 = File(exists=True,  desc='coclass matrix in npy format', mandatory=True)
    
    labels_file = File(exists=True,  desc='labels of nodes', mandatory=False)
    threshold = traits.Int(50, usedefault = True, desc='What min coclass value is reresented by an edge on the graph', mandatory=False)
    gm_mask_coords_file = File(exists=True,  desc='node coordinates in MNI space (txt file)', mandatory=False)
    
class PlotIGraphConjCoclassOutputSpec(TraitedSpec):
    
    plot_igraph_conj_signif_coclass_matrix_file = File(exists=True, desc="eps file with igraph spatial representation")
    plot_igraph_FR_conj_signif_coclass_matrix_file = File(exists=True, desc="eps file with igraph topological representation")
    
class PlotIGraphConjCoclass(BaseInterface):
    
    """
    Description:
    
    Plot coclassification matrix with igraph
    - labels are optional, 
    - threshold is optional (default, 50 = half the group)
    - coordinates are optional, if no coordinates are specified, representation in topological (Fruchterman-Reingold) space
    
    
    Comments:
    
    Not sure it is still used somewhere...
    
    """
    input_spec = PlotIGraphConjCoclassInputSpec
    output_spec = PlotIGraphConjCoclassOutputSpec

    def _run_interface(self, runtime):
                
        print('in plot_coclass')
        
        coclass_matrix_file1 = self.inputs.coclass_matrix_file1
        coclass_matrix_file2 = self.inputs.coclass_matrix_file2
        labels_file = self.inputs.labels_file
        
        threshold = self.inputs.threshold
        gm_mask_coords_file = self.inputs.gm_mask_coords_file
            
        
        #from nipype.utils.filemanip import split_filename as split_f
        
        print('loading labels')
        
        labels = [line.strip() for line in open(labels_file)]
        
        
        print('loading coclass_matrices')
        coclass_matrix1 = np.load(coclass_matrix_file1)
        coclass_matrix2 = np.load(coclass_matrix_file2)
        
        path,fname,ext = split_f(coclass_matrix_file1)
        
        
        print('loading gm mask corres')
        
        gm_mask_coords = np.array(np.loadtxt(gm_mask_coords_file),dtype = 'float')
        
        print(gm_mask_coords.shape)
            
            
        print('computing diff coclass')
        
        if not check_np_shapes(coclass_matrix1.shape,coclass_matrix2.shape):
            
            print("$$$$$$$$ exiting, unequal shapes for coclass matrices")
            
            sys.exit()
            
        diff_matrix = coclass_matrix1 - coclass_matrix2
        
        #### 
        print("plotting diff matrix")    
        
        plot_diff_coclass_matrix_file =  os.path.abspath('heatmap_diff_coclass_matrix.eps')
        
        plot_ranged_cormat(plot_diff_coclass_matrix_file,diff_matrix,labels,fix_full_range = [-50,50])
        
        
        
        print("separating the overlap and signif diff netwtorks")
        
        conj_labelled_matrix = np.zeros(shape = diff_matrix.shape, dtype = 'int')
        
        conj_labelled_matrix[np.logical_and(coclass_matrix1 > threshold,coclass_matrix2 > threshold)] = 1
        
        if  np.sum(conj_labelled_matrix != 0) != 0:
                
            plot_igraph_conj_coclass_matrix_file = os.path.abspath('plot_igraph_3D_conj_coclass_matrix.eps')
            
            plot_3D_igraph_int_mat(plot_igraph_conj_coclass_matrix_file,conj_labelled_matrix,gm_mask_coords,labels = labels)
            
            plot_igraph_FR_conj_coclass_matrix_file = os.path.abspath('plot_igraph_FR_conj_coclass_matrix.eps')
            
            plot_3D_igraph_int_mat(plot_igraph_FR_conj_coclass_matrix_file,conj_labelled_matrix,labels = labels)
            
        ## signif coclass1
        
        signif_coclass1_labelled_matrix = np.zeros(shape = diff_matrix.shape, dtype = 'int')
        
        signif_coclass1_labelled_matrix[np.logical_and(coclass_matrix1 > threshold,diff_matrix > 25)] = 1
        
        if np.sum(signif_coclass1_labelled_matrix != 0) != 0:
            
            plot_igraph_signif_coclass1_coclass_matrix_file = os.path.abspath('plot_igraph_3D_signif_coclass1_coclass_matrix.eps')
            
            plot_3D_igraph_int_mat(plot_igraph_signif_coclass1_coclass_matrix_file,signif_coclass1_labelled_matrix,gm_mask_coords,labels = labels)
            
            plot_igraph_FR_signif_coclass1_coclass_matrix_file = os.path.abspath('plot_igraph_FR_signif_coclass1_coclass_matrix.eps')
            
            plot_3D_igraph_int_mat(plot_igraph_FR_signif_coclass1_coclass_matrix_file,signif_coclass1_labelled_matrix,labels = labels)
            
        
        ## signif coclass2
        
        signif_coclass2_labelled_matrix = np.zeros(shape = diff_matrix.shape, dtype = 'int')
        
        signif_coclass2_labelled_matrix[np.logical_and(coclass_matrix2 > threshold,diff_matrix < -25)] = 1
        
        
        if np.sum(signif_coclass2_labelled_matrix != 0) != 0:
        
            plot_igraph_signif_coclass2_coclass_matrix_file = os.path.abspath('plot_igraph_3D_signif_coclass2_coclass_matrix.eps')
        
            plot_3D_igraph_int_mat(plot_igraph_signif_coclass2_coclass_matrix_file,signif_coclass2_labelled_matrix,gm_mask_coords,labels = labels)
        
            plot_igraph_FR_signif_coclass2_coclass_matrix_file = os.path.abspath('plot_igraph_FR_signif_coclass2_coclass_matrix.eps')
        
            plot_3D_igraph_int_mat(plot_igraph_FR_signif_coclass2_coclass_matrix_file,signif_coclass2_labelled_matrix,labels = labels)
        
        
        print("computing signif int_labelled_signif_matrix")
            
        int_labelled_signif_matrix = np.zeros(shape = diff_matrix.shape, dtype = 'int')
        
        #int_labelled_signif_matrix[np.logical_and(coclass_matrix1 > threshold,coclass_matrix2 > threshold)] = 1
        
        #int_labelled_signif_matrix[diff_matrix > 50] = 2
        #int_labelled_signif_matrix[-diff_matrix < -50] = 3
        
        int_labelled_signif_matrix[conj_labelled_matrix == 1] = 1
        
        
        int_labelled_signif_matrix[signif_coclass1_labelled_matrix == 1] = 2
        int_labelled_signif_matrix[signif_coclass2_labelled_matrix == 1] = 3
        
        
        print(int_labelled_signif_matrix)
        
        print('plotting igraph')
        
        if np.sum(int_labelled_signif_matrix != 0) != 0:
                
            plot_igraph_conj_signif_coclass_matrix_file = os.path.abspath('plot_igraph_3D_conj_signif_coclass_matrix.eps')
            
            plot_3D_igraph_int_mat(plot_igraph_conj_signif_coclass_matrix_file,int_labelled_signif_matrix,gm_mask_coords,labels = labels)
            
        
            plot_igraph_FR_conj_signif_coclass_matrix_file = os.path.abspath('plot_igraph_FR_conj_signif_coclass_matrix.eps')
            
            plot_3D_igraph_int_mat(plot_igraph_FR_conj_signif_coclass_matrix_file,int_labelled_signif_matrix,labels = labels)
            
        return runtime
        
    def _list_outputs(self):
        
        outputs = self._outputs().get()
        
        outputs["plot_igraph_conj_signif_coclass_matrix_file"] = os.path.abspath('plot_igraph_3D_conj_signif_coclass_matrix.eps')
        outputs["plot_igraph_FR_conj_signif_coclass_matrix_file"] = os.path.abspath('plot_igraph_FR_conj_signif_coclass_matrix.eps')
        
        return outputs
        
