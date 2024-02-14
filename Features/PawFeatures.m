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

figure(1)
plot(y_hindlimb_L)
legend('hip','knee','ankle','paw','fingers')    

%% Transformation of xyz axes to zero and data management
% [x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
%     z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
%     y_tail, z_tail] = Zeroing_axes(x_body, y_body, z_body, x_forelimb_L,...
%     y_forelimb_L, z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L,...
%     x_tail, y_tail, z_tail);

%% Selection of paw data
x_hindlimb_paw_L = x_hindlimb_L(:,4);
y_hindlimb_paw_L = y_hindlimb_L(:,4); 
z_hindlimb_paw_L = z_hindlimb_L(:,1);

figure(2)
findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');
hlb = findobj(gca,'Type','line', 'tag','Border');
borders = rmmissing(unique([hlb(1).XData; hlb(2).XData]));

[peaks, peaks_pos, peaks_width, peaks_prominence] = ...
    findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');
%% Step analysis

% bring steps to zero
for i = 1:length(borders)
    val = y_hindlimb_paw_L(borders(i));
    if i == 1
        for j = 1:peaks_pos(i)
            y_hindlimb_paw_L(j) = y_hindlimb_paw_L(j) - val;
        end
    else
        if i == length(borders)
            for j = peaks_pos(i-1)+1:length(y_hindlimb_paw_L)
                y_hindlimb_paw_L(j) = y_hindlimb_paw_L(j) - val;
            end
        else
            for j = peaks_pos(i-1)+1:peaks_pos(i)
                y_hindlimb_paw_L(j) = y_hindlimb_paw_L(j) - val;
            end
        end
    end
end

figure(3)
findpeaks(y_hindlimb_paw_L,'MinPeakDistance',0.5,'MinPeakProminence',...
    0.1, 'Annotate','extents','WidthReference','halfheight');

%% step cycle by derivatives
% if derivative very positive on y -> lift off
% lift off defined by whole foot in the air -> look at fingers?

% show video AND position over time

v = 'C:\Users\Simone\Documents\DTU\Work\MouseFeatureExtraction\Videos\Sideview_mouse 35_Run_1.mp4';
v = VideoReader(v);

saveVideo = VideoWriter(...
    'C:\Users\Simone\Documents\DTU\Work\MouseFeatureExtraction\Videos\Sideview_mouse 35_Run_1_Animated'); %open video file
saveVideo.FrameRate = 10;
open(saveVideo)

figure(4)
for i = 1:v.NumFrames
    subplot(5,1,[1,2,3]); % For video
    frame = readFrame(v);
    imshow(frame);
    drawnow;
    axis off;

    subplot(5,1,[4,5]); % For plot
    plot(y_hindlimb_paw_L);
    hold on;
    xlabel('Frames'); 
    ylabel('height');
    grid on;
    line([i i], [0 y_hindlimb_paw_L(i)],[1 1],'LineStyle','-',...
        'Marker','O','LineWidth',2,'Color','red');
    xlim([0,length(y_hindlimb_paw_L)]);
    hold off;

    grab = getframe(gcf);
    writeVideo(saveVideo, grab);

    pause(0)
end

close(saveVideo)
