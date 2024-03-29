function [input_array, file_path, file_name, file_extension] = browse_file(wanted_extension, window_description)
    % Ask the user for a csv file, convert it to a MATLAB array and return
    % it

    %Browse File :
    [file_name_ext,file_path] = uigetfile({strcat('*.', wanted_extension)}, window_description);
    if isequal(file_name_ext,0)
        error('An input file is necessary to continue');
    end

    [~, file_name, file_extension] = fileparts(file_name_ext);

    [input_table] = readtable([file_path,'\',file_name,file_extension]);
    [input_array] = table2array(input_table);
end

