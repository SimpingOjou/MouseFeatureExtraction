%%% Single path %%%
clc;
clear all;
close all;

% Constants
file_name_side = 'Sideview_mouse 35_Run_1.csv';
file_name_ventral = 'Ventralview_mouse 35_Run_1.csv';
file_path = 'C:\Users\Simone\Documents\DTU\Biomechanics\MouseFeatureExtraction\Data';
Sampling = 199;   
% calibration factor to transform pixels in centimeters 
CF = 18.8; % change the calibration factor as needed 

[Time, x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail] = Initialization(file_path, file_name_side,...
    file_name_ventral, CF, Sampling);

figure(1)
plot(y_hindlimb_L)
xlabel('x [cm]')
ylabel('y [cm]')
legend('hip','knee','ankle','paw','fingers')    

%% Selection of paw and finger data
x_hindlimb_paw_L = x_hindlimb_L(:,4);
y_hindlimb_paw_L = y_hindlimb_L(:,4); 
y_hindlimb_fingers_L = y_hindlimb_L(:,5); 
z_hindlimb_paw_L = z_hindlimb_L(:,1);

figure(2)
findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');
hlb_paw = findobj(gca,'Type','line', 'tag','Border');
borders_paw = rmmissing(unique([hlb_paw(1).XData; hlb_paw(2).XData]));

[peaks_paw, peaks_pos_paw, peaks_width_paw, peaks_prominence_paw] = ...
    findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');

figure(3)
findpeaks(y_hindlimb_fingers_L,'MinPeakDistance',5,'MinPeakProminence',...
    0.2, 'Annotate','extents','WidthReference','halfheight');
hlb_fing = findobj(gca,'Type','line', 'tag','Border');
borders_fing = rmmissing(unique([hlb_fing(1).XData, hlb_fing(2).XData]))';

[peaks_fing, peaks_pos_fing, peaks_width_fing, peaks_prominence_fing] = ...
    findpeaks(y_hindlimb_fingers_L,'MinPeakDistance',5,'MinPeakProminence',...
    0.2, 'Annotate','extents','WidthReference','halfheight');

%% Step analysis

v_fing = diff(y_hindlimb_fingers_L)./diff(Time);
% border is minimum condition filters out local minimums
borders_fing = borders_fing(v_fing(borders_fing) == 0); 
v_threshold_lift = 5; %cm/s
plot_thresh = v_threshold_lift * ones(1, length(v_fing));


figure(4)
plot(v_fing, 'LineWidth', 1.5);
hold on;
scatter(peaks_pos_fing, v_fing(peaks_pos_fing-1), "filled");
scatter(peaks_pos_paw, v_fing(peaks_pos_paw-1),"filled");
plot(plot_thresh, 'LineWidth',2);
scatter(borders_paw, v_fing(borders_paw),'LineWidth',2)
scatter(borders_fing, v_fing(borders_fing),'LineWidth',2)
legend({'v-fing','peak-pos-fingers','peak-pos-paw',...
    'v-threshold', 'borders-paw', 'borders-fing'},"Location","southeast");
xlabel('Time [Frames]')
ylabel('Velocity [cm/s]')
hold off;

% figure(4)
% plot(v_fing, 'LineWidth', 1.5);
% hold on;
% plot(plot_thresh, 'LineWidth',2);
% scatter(find(v_fing>v_threshold_lift), v_fing(v_fing > v_threshold_lift),"filled");
% legend({'finger velocity','v threshold','possible swing startpoints'},"Location","southeast");
% xlabel('Time [Frames]')
% ylabel('Velocity [cm/s]')
% hold off;

touchdowns = []; 
for i = 1:length(borders_fing)
    if borders_paw(i) < borders_fing(i) 
        touchdowns = [touchdowns, borders_paw(i)];
    else 
        touchdowns = [touchdowns, borders_fing(i)]; 
    end
end

% SWINGS
swings = [];
for i = 1:length(peaks_pos_fing) % somehow works better with peaks_pos_paw
    for j = round(peaks_pos_fing(i) - max(peaks_width_fing)/2): peaks_pos_fing(i)
        % fingers are lifting
        if v_fing(j-1) > v_threshold_lift 
            % paw is lifting. If index + range intersects a peak ->
            % complete lift
            if j + (max(peaks_width_fing)/2) >= peaks_pos_paw(i) 
                swings = [swings, j-1];
                break;
            end
        end
    end
end

figure(5)
hold on;
plot(y_hindlimb_fingers_L,'LineWidth', 2)
plot(y_hindlimb_paw_L,'LineWidth', 2)
scatter(swings, y_hindlimb_fingers_L(swings),"filled", 'r',...
        'LineWidth', 2, 'Marker', '^')
    scatter(touchdowns, y_hindlimb_fingers_L(touchdowns),"filled", 'b',...
        'LineWidth', 2, 'Marker', 'v')
    scatter(swings, y_hindlimb_paw_L(swings),"filled", 'r',...
        'LineWidth', 2, 'Marker', '^')
    scatter(touchdowns, y_hindlimb_paw_L(touchdowns),"filled", 'b',...
        'LineWidth', 2, 'Marker', 'v')
xline(swings,'--')
xline(touchdowns,'--')
legend({'fingers','paw','swings','touchdowns'})
xlabel('Time [Frames]')
ylabel('y [cm]')
hold off

% TODO: change borders function bc faulty

%% show video AND position over time

v = 'C:\Users\Simone\Documents\DTU\Biomechanics\MouseFeatureExtraction\Videos\Sideview_mouse 35_Run_1.mp4';
v = VideoReader(v);

saveVideo = VideoWriter(...
    'C:\Users\Simone\Documents\DTU\Biomechanics\MouseFeatureExtraction\Videos\Sideview_mouse 35_Run_1_Animated2'...
    ,'MPEG-4'); %open video file
saveVideo.FrameRate = 30;
open(saveVideo)

figure(6)
set(4,'units','pixels','position',[0 0 1280 1024])
for i = 1:v.NumFrames
    subplot(5,1,[1,2,3]); % For video
    frame = readFrame(v);
    imshow(fliplr(frame));
    drawnow;
    axis off;

    subplot(5,1,[4,5]); % For plot
    plot(y_hindlimb_paw_L);
    hold on;
    plot(y_hindlimb_fingers_L);

    scatter(swings, y_hindlimb_fingers_L(swings),"filled", 'r',...
        'LineWidth', 2, 'Marker', '^')
    scatter(touchdowns, y_hindlimb_fingers_L(touchdowns),"filled", 'b',...
        'LineWidth', 2, 'Marker', 'v')
    scatter(swings, y_hindlimb_paw_L(swings),"filled", 'r',...
        'LineWidth', 2, 'Marker', '^')
    scatter(touchdowns, y_hindlimb_paw_L(touchdowns),"filled", 'b',...
        'LineWidth', 2, 'Marker', 'v')

    xlabel('x [cm]'); 
    ylabel('y [cm]');
    grid on;
    line([i i], [0 y_hindlimb_paw_L(i)],[1 1],'LineStyle','-',...
        'LineWidth',1,'Color',[0.4660 0.6740 0.1880],...
        'Marker','*');
    xlim([0,length(y_hindlimb_paw_L)]);
    legend({'paw position','finger position','swing point',...
        'touchdown point','','',''})
    hold off;

    grab = getframe(gcf);
    writeVideo(saveVideo, grab);

    pause(0)
end

close(saveVideo)
