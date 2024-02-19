%%% Single path %%%
clc;
clear all;
close all;

% Constants
% file_name_side = 'Sideview_mouse 35_Run_1.csv';
% file_name_ventral = 'Ventralview_mouse 35_Run_1.csv';
% file_path = 'C:\Users\Simone\Documents\DTU\Work\MouseFeatureExtraction\Data';

% Ask the user for the input data files
[input_array_side, file_path_side, file_name_side, file_extension_side] = browse_file('csv', 'Side view input data file');
[input_array_ventral, file_path_ventral, file_name_ventral, file_extension_ventral] = browse_file('csv', 'Ventral view input data file');

file_path = file_path_side;
file_name_ext_side = strcat(file_name_side, file_extension_side);
file_name_ext_ventral = strcat(file_name_ventral, file_extension_ventral);

Sampling = 199;   
% calibration factor to transform pixels in centimeters 
CF = 18.8; % change the calibration factor as needed 

[Time, x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail] = Initialization(file_path, file_name_ext_side,...
    file_name_ext_ventral, CF, Sampling);

%% Plot all the points

delay = 0.1;
% Limits of the plot [x_min x_max y_min y_max]
plot_limits = [-36 -20 -8 -5];

frame_nbr = size(Time);
frame_nbr = frame_nbr(1);

close all;
h = figure;
hold on
grid
%axis(plot_limits)
for i=1:frame_nbr
    cla()
    
    points_x = {x_body(i,:); x_forelimb_L(i,:); x_hindlimb_L(i,:); x_tail(i,:)};
    points_y = {y_body(i,:); y_forelimb_L(i,:); y_hindlimb_L(i,:); y_tail(i,:)};

    plot_points_and_angles(points_x, points_y, [])

    drawnow()
    pause(delay)

    if ~ishandle(h)
        break
    end
end
      
%% transformation of xyz axes to zero 
% arrays = {x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
%     z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
%     y_tail, z_tail};  % Store arrays in a cell array

[x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail] = Zeroing_axes(x_body, y_body, z_body, x_forelimb_L,...
    y_forelimb_L, z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L,...
    x_tail, y_tail, z_tail);

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
figure(1)
findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');

% get border from plot
hlb = findobj(gca,'Type','line', 'tag','Border');
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
v_vector_sd = std(v_vector);

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
a_vector_sd = std(a_vector);
% TODO: rappresentazione a cerchhio dello step cycle xyt
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
velocity_paw_L = Hypot3D(diff(x_hindlimb_paw_L)./diff(Time),...
    diff(y_hindlimb_paw_L)./diff(Time),...
    diff(z_hindlimb_paw_L)./diff(Time));
max_v = max(velocity_paw_L);
% plot(Time(1:end-1),velocity_over_time);
% plot(x_hindlimb_L',y_hindlimb_L') % remove outliers
% max_v(inv) =
% 
%    41.2284
% max_v(2D) =
% 
%   217.2496 % there are strange peaks
% max_v(3D) =
% 
%   217.4858

 % figure(2)
 % plot3(x_hindlimb_paw_L, y_hindlimb_paw_L, z_hindlimb_paw_L, 'LineWidth', 2);
 % xlabel('x')
 % ylabel('y')
 % zlabel('z')

% figure(3)
% plot3(v_vector(1), v_vector(2), v_vector(3), 'LineWidth', 2)
% xlabel('x')
% ylabel('y')
% zlabel('z')
% 
% figure(4)

%% TODO: differentiate step cycle in stance (touch down) and swing (lift off)
% IDEA: calculate border, then define touch down and lift off ass
% parameters that are controlled by the proportion wrt peak-valley height
% and define them on the time vector

% TODO: appiattire il segnale e gestire paralitici

[peaks, peaks_pos, peaks_width, peaks_prominence] = ...
    findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');

steps = borders(1:end-1);
valleys = y_hindlimb_paw_L(steps);
proms = peaks - valleys; % not using the default one bc it's strange
stance_threshold = 0.015 * proms; % by eye
swing_threshold = 0.015 * proms;

stances_start = [];
swings_start = [];
temp = peaks_pos(1);
timesteps = 5; % change based on needs

for i=1:length(steps)
    for j=1:timesteps
        diff = y_hindlimb_paw_L(steps(i) - j) - valleys(i);
        if  diff > stance_threshold(i)
            stances_start(end+1) = steps(i) - j;
            break;
        end
    end
end

for i=1:length(steps)
    for j=1:timesteps
        diff = y_hindlimb_paw_L(steps(i) + j) - valleys(i);
        if  diff > swing_threshold(i)
            swings_start(end+1) = steps(i) + j;
            break;
        end
    end
end

figure(2);
plot(Frames(1:end-1),y_hindlimb_paw_L, 'LineWidth', 1.5);
hold on;
scatter(peaks_pos, peaks, 40, "x", 'LineWidth', 1);
scatter(borders, y_hindlimb_paw_L(borders), 40, 'LineWidth', 1.5);
scatter(swings_start, y_hindlimb_paw_L(swings_start), 40, 'LineWidth', 1.5)
scatter(stances_start, y_hindlimb_paw_L(stances_start), 40,'LineWidth', 1.5)
xlabel('Frames (fps)');
ylabel('Height (y)');
title('Findpeak non inverted');
legend('y pose', 'peaks', 'borders', 'swings startpoints', 'stances startpoints');
ylim([min(y_hindlimb_paw_L), max(y_hindlimb_paw_L)]);
xlim([0,Frames(end-1)]);
grid on;
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

%% Hindlimb joint angles

% body : head, spine 0% (neck base), spine 25%, spine 50%, spine 75%, tail base
% forelimb : shoulder, elbow, wrist, forepaw
% hindlimb : hip, knee, anckle, hindpaw, hindfingers
% tail : tail base, tail 25%, tail 50%, tail 75%, tail 100%.

% Calculate the vectors corresponding to the parts of the hind limb

% 3D matrix containing (limb part id, frame id, x or y coordinate)
% With limb part id : 1=l_spine_hip, 2=l_hip_knee, 3=l_knee_anckle,
% 4=l_anckle_hindpaw, 5=l_hindpaw_hindfinger
hindlimb_vectors = get_vectors_from_pos([x_body(:, 5) x_hindlimb_L], [y_body(:, 5) y_hindlimb_L]);

% To access the vector corresponding to hip-shoulder, use
%   squeeze(hindlimb_vectors(1,:,:))

% Vector corresponding to the ground direction, opposite to the movement
ground_vec = [-1 0];

% Get the angles on each frame (in rad)
% hindlimb_joint_angles is of shape : (joint id, frame id)
% With joint id : 1=hip, 2=knee, 3=anckle, 4=hindpaw
hindlimb_joint_angles = successive_angles(hindlimb_vectors, ground_vec);

%% Forelimb joint angles
% body : head, spine 0% (neck base), spine 25%, spine 50%, spine 75%, tail base
% forelimb : shoulder, elbow, wrist, forepaw
% hindlimb : hip, knee, anckle, hindpaw, hindfingers
% tail : tail base, tail 25%, tail 50%, tail 75%, tail 100%.

% 3D matrix containing (limb part id, frame id, x or y coordinate)
% With limb part id : 1=l_spine_hip, 2=l_hip_knee, 3=l_knee_anckle,
% 4=l_anckle_hindpaw, 5=l_hindpaw_hindfinger
forelimb_vectors = get_vectors_from_pos([x_body(:, 4) x_forelimb_L], [y_body(:, 4) y_forelimb_L]);

% Vector corresponding to the ground direction, opposite to the movement
ground_vec = [-1 0];

% Get the angles on each frame (in rad)
% forelimb_joint_angles is of shape : (joint id, frame id)
% With joint id : 1=hip, 2=knee, 3=anckle, 4=hindpaw
forelimb_joint_angles = successive_angles(forelimb_vectors, ground_vec);

%% Display the joint angles (animated)

r = 0.1;        % Radius of the circle in the plot representing the angles
delay = 0.1;    % Delay between frames to display (= second per frame)
% Limits of the plot [x_min x_max y_min y_max]
plot_limits = [-2 2.5 -2 1.5];

close all;
h = figure;
grid
%axis(plot_limits)
ang_size = size(hindlimb_joint_angles(1,:));
for i=1:ang_size(2)
    cla()

    points_x = {x_body(i,:); x_forelimb_L(i,:); x_hindlimb_L(i,:); x_tail(i,:)};
    points_y = {y_body(i,:); y_forelimb_L(i,:); y_hindlimb_L(i,:); y_tail(i,:)};

    angles = {[], squeeze(forelimb_joint_angles(2:end,i)), squeeze(hindlimb_joint_angles(2:end,i)), []};

    plot_points_and_angles(points_x, points_y, angles)

    drawnow()
    pause(delay)

    if ~ishandle(h)
        break
    end
end

%%  create summary table with all values %%%
Step_cycle_features = padcat(step_duration, step_frequency ,step_height, step_length, step_speed);
Step_cycle_Features = array2table(Step_cycle_features);
Step_cycle_Features.Properties.VariableNames(1:5) = {'Step_Cycle_Duration', 'Step_Frequency', 'Step_Height', 'Step_Length', 'Step_speed'};
%%
writetable(Step_cycle_Features,[file_path,'\',file_name_side, '_Step_cycle_Features_.csv']);
save ([file_path,'\',file_name_side, '_Step_cycle_Features_.Mat'])
