%%% Single path %%%
clc;
clear all;
close all;

%Browse File :
% [file_name,file_path] = uigetfile({'*.csv'}); 
% file_name = char(file_name);
% file_path = char(file_path);
file_name_side = 'Sideview_mouse 35_Run_1.csv';
file_name_ventral = 'Ventralview_mouse 35_Run_1.csv';
file_path = 'C:\Users\Simone\Documents\DTU\Work\MouseFeatureExtraction\Data';
% input = dir([file_path,'\*.csv']);
% tStrF = strfind(file_path,'\');

[Corridor_Side] = table2array(readtable([file_path,'\',file_name_side]));
[Corridor_Ventral] = table2array(readtable([file_path,'\',file_name_ventral]));

if length(Corridor_Ventral) == length(Corridor_Side)
    Frames = Corridor_Side(:,1);                     % extract frame column
else
    fprintf('WARNING: The two videos have different frame numbers!')
end

Sampling = 199;                           % frequency of acquisition
Time = Frames * (1/Sampling);
Likelihood = [Corridor_Side(:,4:3:end), Corridor_Ventral(:,4:3:end)]; % extract likelihood 

%% calibration factor to transform pixels in centimeters 
CF = 18.8; % change the calibration factor as needed 

% markers name in the columns for the body: Head, Spine 1, Spine 2, Spine 3, Spine 4,Base
x_body = -1 * Corridor_Side(:,[2, 5, 8, 11, 14, 17]) / CF; % extract x columns for body 
y_body = -1 * Corridor_Side(:,[3, 6, 9, 12, 15, 18]) / CF; % extract y columns for body 

% should there be a check on the first frame where I see if it's different
% on the shared x axis?

z_body = -1 * Corridor_Ventral(:,[3, 6, 9, 12, 15, 18]) / CF;

%%% markers name in the columns for the forelimb: shoulder, elbow, wrist, lForepaw
x_forelimb_L = -1 * Corridor_Side(:,[32, 35, 38, 41]) / CF;  % extract x columns for left forelimb
y_forelimb_L = -1 * Corridor_Side(:,[33, 36, 39, 42]) / CF;  % extract y columns for left forelimb

z_forelimb_L = -1 * Corridor_Ventral(:,33) / CF;

%%% markers name in the columns for the hindlimb: hip, knee, anckle, lHindpaw, lHindfingers
x_hindlimb_L = -1 * Corridor_Side(:,[44, 47, 50, 53, 56]) / CF;  % extract x columns for left hindlimb
y_hindlimb_L = -1 * Corridor_Side(:,[45, 48, 51, 54, 57]) / CF;  % extract y columns for left hindlimb

z_hindlimb_L = -1 * Corridor_Ventral(:,[39, 42]) / CF;

%%% markers name in the columns for the tail: tail 25%, tail 50%, tail 75%, tail 100%. 
x_tail = -1 * Corridor_Side(:,[17, 20, 23, 26, 29]) / CF; % extract x columns for tail, 
y_tail = -1 * Corridor_Side(:,[18, 21, 24, 27, 30]) / CF; % extract y columns for tail

z_tail = -1 * Corridor_Ventral(:,[18, 21, 24, 27, 30]) / CF;
      
%% transformation of xyz axes to zero 
arrays = {x_body, x_forelimb_L, x_hindlimb_L, x_tail, y_body, y_forelimb_L,...
    y_hindlimb_L, y_tail, z_body, z_forelimb_L, z_hindlimb_L};  % Store arrays in a cell array

for i = 1:numel(arrays)
    min_value = min(min(arrays{i}));

    % Subtract the minimum value from all elements
    arrays{i} = arrays{i} - min_value;
end

% TODO: plot the arrays

x_body = arrays{1};
x_forelimb_L = arrays{2};
x_hindlimb_L = arrays{3};
x_tail = arrays{4};
y_body = arrays{5};
y_forelimb_L = arrays{6};
y_hindlimb_L = arrays{7};
y_tail = arrays{8};
z_body = arrays{9};
z_forelimb_L = arrays{10};
z_hindlimb_L = arrays{11};

%% mean speed of the body along the run

% Instantaneous speed 
Speed_Inst = hypot(diff(x_body), diff(y_body))./diff(Time);   
Speed_Mean = movmean(Speed_Inst,100); % remove peaks
% mean speed of all points in the body
Speed_mean_fin = mean(Speed_Mean,2);             

[n,m] = size(Time);
Time = ([Time(2:end,:)]);
%%  Feature calculation

% 1) Foot trajectory 
% TOASK: why from 2:end?
x_forelimb_foot_L = x_forelimb_L(2:end,4); 
y_forelimb_foot_L = y_forelimb_L(2:end,4); 
x_body_foot = x_body(2:end,2:end);
y_body_foot = y_body(2:end,2:end);
x_hindlimb_paw_L = x_hindlimb_L(2:end,4);
y_hindlimb_paw_L = y_hindlimb_L(2:end,4); 
z_hindlimb_paw_L = z_hindlimb_L(2:end,1);

y_hindlimb_L_inv = -y_hindlimb_paw_L + 1; % to find valleys
 
% findpeaks(y_hindlimb_L_inv,'MinPeakDistance',0.5,'MinPeakProminence',0.1, 'Annotate','extents','WidthReference','halfheight')
% xlabel('Frames (fps)')
% ylabel('Height (y)')
% title('Findpeak inverted');
% hold off; 

[peak_amplitudes, peak_amplitudes_pos, peak_width, peak_prominence] = ...
    findpeaks(y_hindlimb_L_inv,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');

% 2) step cycle duration
peaktime = (peak_amplitudes_pos*(1/Sampling));
step_duration = diff(peaktime);
step_duration_mean = mean(step_duration); 
step_duration_sd = std(step_duration); 
step_duration_n = length(step_duration);          

% 3) step frequency
step_frequency = 1 ./ step_duration; 
step_frequency_mean = mean(step_frequency); 
step_frequency_sd = std(step_frequency); 
step_frequency_n = length(step_frequency);          

% 4) step height
step_height = peak_prominence(2:end,:); 
step_height_mean = mean(step_height); 
step_height_sd = std(step_height); 
step_height_n = length(step_height);        

% 5) step length
step_x = x_hindlimb_paw_L(peak_amplitudes_pos);
step_length = diff(step_x);

% 6) body speed
step_speed = Speed_mean_fin(peak_amplitudes_pos(2:end,:));

% 7) Endpoint path length 
findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight')
xlabel('Frames (fps)')
ylabel('Height (y)')
title('Findpeak non inverted');
% get border from plot
Ax = gca;
hlb = findobj(Ax,'Type','line', 'tag','Border');
borders = rmmissing(unique([hlb(1).XData; hlb(2).XData]));

% TODO: divide per step
ep_path_length = hypot(diff(x_hindlimb_paw_L), diff(y_hindlimb_paw_L)); 
ep_path_length_sd = std(ep_path_length);

% 8) Endpoint velocity vector orientation at swing onset
step_startpoints = borders(1:end-1); % there is one extra border

% +3 steps bc can't see the difference otherwise on y [cm/sec]
v_vector = [(x_hindlimb_paw_L(step_startpoints + 3) - ...
    x_hindlimb_paw_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)) ,...
    (y_hindlimb_paw_L(step_startpoints + 3) -...
    y_hindlimb_paw_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)) ,...
    (z_hindlimb_paw_L(step_startpoints + 3) -...
    z_hindlimb_paw_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints))]; 

v_orientation_rad = [atan2(v_vector(:,2), v_vector(:,1)),...
    atan2(v_vector(:,3), v_vector(:,2))]; % tg(y/x) & tg(z/y)
v_orientation_deg = rad2deg(v_orientation_rad);
v_vector_sd = std(v_vector_deg);

% 9) Endpoint acceleration vector orientation at swing onset
a_vector = [(x_hindlimb_paw_L(step_startpoints + 3) - ...
    x_hindlimb_paw_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)).^2 ,...
    (y_hindlimb_paw_L(step_startpoints + 3) -...
    y_hindlimb_paw_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)).^2 ,...
    (z_hindlimb_paw_L(step_startpoints + 3) -...
    z_hindlimb_paw_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)).^2]; 

a_orientation_rad = [atan2(a_vector(:,2), a_vector(:,1)),...
    atan2(a_vector(:,3), a_vector(:,2))];
a_orientation_deg = rad2deg(a_orientation_rad);
a_vector_sd = std(a_vector_deg);

%       x          y        z
% v_vector(inv) =
%     7.2945    4.5018
%    40.5780    2.1673
%    19.3118    3.3110
%    40.3180    0.2047
%    38.8511    4.9435
%    39.7109    3.6928
%    35.6536    0.5403
%    33.6943    0.1508
% v_orientation_deg(inv) =
% 
%    31.6807 
%     3.0573
%     9.7287
%     0.2909
%     7.2514
%     5.3128
%     0.8682
%     0.2564
% v_vector(3D) =
% 
%     1.5551    0.7225    3.6575
%     2.7217         0    0.4805
%     2.1608    1.1616    0.5723
%     3.4191    0.0768    0.3342
%     3.5833    0.6378   -0.1054
%     2.5439    2.5385   -0.3730
%     1.9492    2.9533    0.1292
% v_orientation_deg(3D) =
% 
%    24.9188   78.8263
%          0   90.0000
%    28.2613   26.2273
%     1.2863   77.0614
%    10.0921   -9.3831
%    44.9393   -8.3590
%    56.5749    2.5042

% a_vector(inv) =
%    1.0e+03 *
%     0.4839    0.2986
%     2.6917    0.1438
%     1.2810    0.2196
%     2.6744    0.0136
%     2.5771    0.3279
%     2.6342    0.2450
%     2.3650    0.0358
%     2.2351    0.0100
% a_vector(3D) =
% 
%   103.1533   47.9232  242.6142
%   180.5362         0   31.8720
%   143.3304   77.0507   37.9593
%   226.7987    5.0927   22.1670
%   237.6912   42.3056   -6.9908
%   168.7437  168.3866  -24.7419
%   129.2952  195.8999    8.5675

% 10) Max limb endpoint velocity
% max_v = max(hypot(v_vector(1), v_vector(2))); % velocity over the direction
velocity_over_time = hypot(diff(x_hindlimb_paw_L)./diff(Time), diff(y_hindlimb_paw_L)./diff(Time));
max_v = max(velocity_over_time);
% plot(Time(1:end-1),velocity_over_time);
% max_v(inv) =
% 
%    41.2284
% max_v(2D) =
% 
%   217.2496 % there are strange peaks

% TODO: differentiate step cycle in stance (touch down) and swing (lift off)
% IDEA: calculate border, then define touch down and lift off ass
% parameters that are controlled by the proportion wrt peak-valley height
% and define them on the time vector
%% clustering of steps features_Height 

% Step_Heigth_max = max (peak_prominence);      %find max value for thresholding
% T1= (((step_height_mean)/100)*70);         % (70%of the mean value)
% T2= (((step_height_mean)/100)*40);         %(70%of the mean value)

%Absolute threshold 
T1 = 0.75;
T2 = 0.25;

% Split steps based on amplitude thresholds
Steps_Heigth_Low = peak_prominence(peak_prominence < T2);         % Split steps with low amplitude 
Steps_Heigth_Medium = peak_prominence(peak_prominence > T2 & peak_prominence < T1);   % Split steps with medium amplitude 
Steps_Height_High = peak_prominence(peak_prominence > T1);        % Split steps with high amplitude

Steps_Impaired_Number = length(Steps_Heigth_Low);   % Only steps with low amplitude
Steps_Impaired_Amplitude_mean = mean(Steps_Heigth_Low);   % Only steps with low amplitude
Steps_Impaired_Amplitude_sd = std(Steps_Heigth_Low);   % Only steps with low amplitude

Steps_Functional_Number = length(Steps_Heigth_Medium);    % Only steps with medium amplitude
Steps_Functional_Amplitude_mean = mean(Steps_Heigth_Medium);    % Only steps with medium amplitude
Steps_Functional_Amplitude_sd = std(Steps_Heigth_Medium);    % Only steps with medium amplitude

Steps_Propulsive_Number = length(Steps_Height_High);      % Only steps with large amplitude
Steps_Propulsive_Amplitude_mean = mean(Steps_Height_High);      % Only steps with large amplitude
Steps_Propulsive_Amplitude_sd = std(Steps_Height_High);      % Only steps with large amplitude

%%  create summary table with all values %%%
Step_cycle_features = padcat(step_duration, step_frequency ,step_height, step_length, step_speed);
Step_cycle_Features = array2table(Step_cycle_features);
Step_cycle_Features.Properties.VariableNames(1:5) = {'Step_Cycle_Duration', 'Step_Frequency', 'Step_Height', 'Step_Length', 'Step_speed'};
%%
writetable(Step_cycle_Features,[file_path,'\',file_name_side, '_Step_cycle_Features_.csv']);
save ([file_path,'\',file_name_side, '_Step_cycle_Features_.Mat'])
