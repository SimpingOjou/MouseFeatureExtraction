%%% Single path %%%
clc;
clear all;
close all;

%Browse File :
[file_name,file_path] = uigetfile({'*.csv'}); 
file_name = char(file_name);
file_path = char(file_path);
input = dir([file_path,'\*.csv']);
tStrF = strfind(file_path,'\');
[Corridor_Side_1] = readtable([file_path,'\',file_name]);

[Corridor_Side] = table2array(Corridor_Side_1);
numbers = Corridor_Side (1:end, 1:end);
Frames = numbers(:,1);                     % extract frame column
Sampling = 199;                           % frequency of acquisition
Time = Frames * (1/Sampling);
Likelihood = numbers(:,4:3:end); % extract likelihood for left hindlimb
%% markers name in the columns for the body: Head, Spine 1, Spine 2, Spine 3, Spine 4,Base
x_body = -1 * numbers(:,[2, 5, 8, 11, 14, 17]); % extract x columns for body 
y_body = -1 * numbers(:,[3, 6, 9, 12, 15, 18]); % extract y columns for body 

%%% markers name in the columns for the forelimb: shoulder, elbow, wrist, lForepaw
x_forelimb_L = -1 * numbers(:,[32, 35, 38, 41]);  % extract x columns for left forelimb
y_forelimb_L = -1 * numbers(:,[33, 36, 39, 42]);  % extract y columns for left forelimb

%%% markers name in the columns for the hindlimb: hip, knee, anckle, lHindpaw, lHindfingers
x_hindlimb_L = -1 * numbers(:,[44, 47, 50, 53, 56]);  % extract x columns for left hindlimb
y_hindlimb_L = -1 * numbers(:,[45, 48, 51, 54, 57]);  % extract y columns for left hindlimb

%%% markers name in the columns for the tail: tail 25%, tail 50%, tail 75%, tail 100%. 
x_tail = -1 * numbers(:,[17, 20, 23, 26, 29]); % extract x columns for tail, 
y_tail = -1 * numbers(:,[18, 21, 24, 27, 30]); % extract y columns for tail

%%% calibration factor to transform pixels in centimeters 
CF = 18.8; % change the calibration factor as needed 

% x and y for body
x_body = x_body / CF; y_body = y_body / CF;      
% x and y for forelimb
x_forelimb_L = x_forelimb_L / CF; y_forelimb_L = y_forelimb_L / CF;    
% x and y for hindlimb
x_hindlimb_L = x_hindlimb_L / CF; y_hindlimb_L = y_hindlimb_L / CF;  
% x and y for tail
x_tail = x_tail / CF; y_tail = y_tail / CF;         
%% transformation of x axes to zero 
arrays = {x_body, x_forelimb_L, x_hindlimb_L, x_tail};  % Store arrays in a cell array

for i = 1:numel(arrays)
    % why is the tail not needed?
    min_value = min(min(arrays{i}));

    % Subtract the minimum value from all elements
    arrays{i} = arrays{i} - min_value;
end

x_body = arrays{1};
x_forelimb_L = arrays{2};
x_hindlimb_L = arrays{3};
x_tail = arrays{4};

% transformation of y axes to zero 
arrays = {y_body, y_forelimb_L, y_hindlimb_L, y_tail};  % Store arrays in a cell array

for i = 1:numel(arrays)
    % why is the tail not needed?
    min_value = min(min(arrays{i}));

    % Subtract the minimum value from all elements
    if i ~= 4
        arrays{i} = arrays{i} - min_value;
    end
end

y_body = arrays{1};
y_forelimb_L = arrays{2};
y_hindlimb_L = arrays{3};
y_tail = arrays{4};
%% mean speed of the body along the run  %%%%

% Instantaneous speed 
Speed_Inst = hypot(diff(x_body), diff(y_body))./diff(Time);   
Speed_Mean = movmean(Speed_Inst,100); % remove peaks
% mean speed of all points in the body
Speed_mean_fin = mean(Speed_Mean,2);             

[n,m] = size(Time);
Time = ([Time(2:end,:)]);
%%  Feature calculation

% 1) Foot trajectory 
x_forelimb_L = x_forelimb_L(2:end,4); 
y_forelimb_L = y_forelimb_L(2:end,4); 
x_body = x_body(2:end,2:end);
y_body = y_body(2:end,2:end);
x_hindlimb_L = x_hindlimb_L(2:end,4);
y_hindlimb_L = y_hindlimb_L(2:end,4);

y_hindlimb_L = -y_hindlimb_L + 1; % to find valleys
 
findpeaks(y_hindlimb_L,'MinPeakDistance',0.5,'MinPeakProminence',0.1, 'Annotate','extents','WidthReference','halfheight')
xlabel('Frames (fps)')
ylabel('Height (y)')
title('Findpeak');
% get border from plot
Ax = gca;
hlb = findobj(Ax,'Type','line', 'tag','Border');
borders = rmmissing(unique([hlb(1).XData; hlb(2).XData]));
hold off; 

[peak_amplitudes, peak_amplitudes_pos, peak_width, peak_prominence] = findpeaks(y_hindlimb_L,'MinPeakDistance',0.5,'MinPeakProminence',0.1, 'Annotate','extents','WidthReference','halfheight')

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
step_x = x_hindlimb_L(peak_amplitudes_pos);
step_length = diff(step_x);

% 6) body speed
step_speed = Speed_mean_fin(peak_amplitudes_pos(2:end,:));

% 7) Endpoint path length 
ep_path_length = hypot(diff(x_hindlimb_L), diff(y_hindlimb_L)); % divide per step
ep_path_length_sd = std(ep_path_length);

% ep_path_length_total =
% 
%    28.4338

% 8) Endpoint velocity vector orientation at swing onset
step_startpoints = borders(1:end-1); % there is one extra border

% +3 steps bc can't see the difference otherwise on y [cm/sec]
v_vector = [(x_hindlimb_L(step_startpoints + 3) - ...
    x_hindlimb_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)) ,...
    (y_hindlimb_L(step_startpoints + 3) -...
    y_hindlimb_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints))]; % orientation given by the sign

v_orientation_rad = atan2(v_vector(:,2), v_vector(:,1));
v_orientation_deg = rad2deg(v_orientation_rad);
v_vector_sd = std(v_orientation);

% v_orientation_deg =
% 
%    31.6807 this looks strange
%     3.0573
%     9.7287
%     0.2909
%     7.2514
%     5.3128
%     0.8682
%     0.2564

% 9) Endpoint acceleration vector orientation at swing onset
a_vector = [(x_hindlimb_L(step_startpoints + 3) - ...
    x_hindlimb_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)).^2 ,...
    (y_hindlimb_L(step_startpoints + 3) -...
    y_hindlimb_L(step_startpoints)) ./ ...
    (Time(step_startpoints + 3) - Time(step_startpoints)).^2]; % orientation given by the sign

a_orientation_rad = atan2(a_vector(:,2), a_vector(:,1));
a_orientation_deg = rad2deg(a_orientation_rad);
a_vector_sd = std(a_orientation);

% Values seem a bit high
%       x          y
% v_vector =
%     7.2945    4.5018
%    40.5780    2.1673
%    19.3118    3.3110
%    40.3180    0.2047
%    38.8511    4.9435
%    39.7109    3.6928
%    35.6536    0.5403
%    33.6943    0.1508
% a_vector =
%    1.0e+03 *
%     0.4839    0.2986
%     2.6917    0.1438
%     1.2810    0.2196
%     2.6744    0.0136
%     2.5771    0.3279
%     2.6342    0.2450
%     2.3650    0.0358
%     2.2351    0.0100

% 10) Max limb endpoint velocity
max_v = max(hypot(v_vector(1), v_vector(2))); % velocity over the direction

% max_v =
% 
%    41.2284

% some features are not so clear, need extra info
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
writetable(Step_cycle_Features,[file_path,'\',file_name, '_Step_cycle_Features_.csv']);
save ([file_path,'\',file_name, '_Step_cycle_Features_.Mat'])
