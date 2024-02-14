function [] = plot_vec_angle(x1,x2,theta,r)
    % Function adding the vectors x1 and x2 to plot, with the angle theta
    %   between them (shown with a fraction of a circle of radius r)
    
    % Calculate the angles to plot by adding a phase so that the
    %   plotted angle starts at the vector x1
    th = linspace(0, theta);
    th = th - vec_angle(x1, [1 0]);
    xx = r*cos(th); yy = r*sin(th);

    hold on
    plot([0 x1(1)],[0 x1(2)],'r')
    plot([0 x2(1)],[0 x2(2)],'b')
    plot(xx,yy)
end

