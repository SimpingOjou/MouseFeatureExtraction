function [Time, x_body, y_body, z_body, x_forelimb_L, y_forelimb_L,...
    z_forelimb_L, x_hindlimb_L, y_hindlimb_L, z_hindlimb_L, x_tail,...
    y_tail, z_tail] = Initialization(file_path, file_name_side,...
    file_name_ventral, CF, Sampling)
    % default: CF = 18.8 & Sampling = 199
    
    % Read data from CSV files
    Corridor_Side = table2array(readtable(fullfile(file_path, file_name_side)));

    if ~isempty(file_name_ventral)
        Corridor_Ventral = table2array(readtable(fullfile(file_path, file_name_ventral)));

        % Check if the number of frames is the same in both datasets
        if size(Corridor_Ventral, 1) == size(Corridor_Side, 1)
            Frames = Corridor_Side(:, 1);  % Extract frame column
        else
            error('The two videos have different frame numbers!');
        end

        % Extracting marker positions and transforming them (from ventral
        % view)
        z_body = -1 * Corridor_Ventral(:, [3, 6, 9, 12, 15, 18]) / CF;
        z_forelimb_L = -1 * Corridor_Ventral(:, 33) / CF;
        z_hindlimb_L = -1 * Corridor_Ventral(:, [39, 42]) / CF;
        z_tail = -1 * Corridor_Ventral(:, [18, 21, 24, 27, 30]) / CF;
    else
        Frames = Corridor_Side(:, 1); % Extract frame column

        z_body = 0 * Corridor_Side(:, [3, 6, 9, 12, 15, 18]);
        z_forelimb_L = 0 * Corridor_Side(:, 33);
        z_hindlimb_L = 0 * Corridor_Side(:, [39, 42]);
        z_tail = 0 * Corridor_Side(:, [18, 21, 24, 27, 30]);
    end

    Time = Frames / Sampling;
    
    % Extracting marker positions and transforming them
    x_body = -1 * Corridor_Side(:, [2, 5, 8, 11, 14, 17]) / CF; 
    y_body = -1 * Corridor_Side(:, [3, 6, 9, 12, 15, 18]) / CF; 
    
    x_forelimb_L = -1 * Corridor_Side(:, [32, 35, 38, 41]) / CF;  
    y_forelimb_L = -1 * Corridor_Side(:, [33, 36, 39, 42]) / CF;  

    x_hindlimb_L = -1 * Corridor_Side(:, [44, 47, 50, 53, 56]) / CF;  
    y_hindlimb_L = -1 * Corridor_Side(:, [45, 48, 51, 54, 57]) / CF;  

    x_tail = -1 * Corridor_Side(:, [17, 20, 23, 26, 29]) / CF;
    y_tail = -1 * Corridor_Side(:, [18, 21, 24, 27, 30]) / CF; 
end
