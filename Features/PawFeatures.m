%%% Single path %%%
clc;
clear all;
close all;

% Constants
file_name_side = 'Sideview_mouse 35_Run_1.csv';
file_name_ventral = 'Ventralview_mouse 35_Run_1.csv';
file_path = 'C:\Users\Simone\Documents\DTU\Work\MouseFeatureExtraction\Data';
Sampling = 199;   
% calibration factor to transform pixels in centimeters 
CF = 18.8; % change the calibration factor as needed 

[Time, x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail] = Initialization(file_path, file_name_side,...
    file_name_ventral, CF, Sampling);
      
%% transformation of xyz axes to zero 
arrays = {x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail};  % Store arrays in a cell array

[x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail] = Zeroing_axes(x_body, y_body, z_body, x_forelimb_L,...
    y_forelimb_L, z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L,...
    x_tail, y_tail, z_tail);

%% Feature calculation
