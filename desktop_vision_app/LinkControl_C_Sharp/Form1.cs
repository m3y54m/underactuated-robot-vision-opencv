using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO.Ports;

// EmguCV
using Emgu.CV;
using Emgu.CV.Structure;
using Emgu.Util;

using System.Net;

namespace LinkControl_C_Sharp
{
    public partial class Form1 : Form
    {
        Capture capture;
        bool captureInProgress = false;
        int cameraIndex = 1;

        const double hueTolerance = 10;
        const double saturationTolerance = 120;
        const double valueTolerance = 120;

        const int imageWidth = 640;         // in pixels
        const int fieldRealWidth = 215;     // in centimeters

        double ratio = (double)imageWidth / fieldRealWidth;

        const float minDiameter = 4;        // in centimeters
        const float maxDiameter = 10;       // in centimeters

        PointF redCenter = new PointF(0, 0);
        PointF blueCenter = new PointF(0, 0);
        PointF greenCenter = new PointF(0, 0);
        PointF yellowCenter = new PointF(0, 0);

        double redX;
        double redY;

        double blueX;
        double blueY;

        double yellowX;
        double yellowY;

        double dt = 40;          // in miliseconds
        double error = 0;        // in centimeters
        double last_error = 0;   // in centimeters

        double error1 = 0;
        double error2 = 0;
        double last = 0;

        bool isFirstFrame = true;

        Image<Bgr, byte> BgrOrColors;

        public class commonColors
        {
                public Bgr Red = new Bgr();
                public Bgr Blue = new Bgr();
                public Bgr Green = new Bgr();
                public Bgr Yellow = new Bgr();
                public Bgr Purple = new Bgr();
                public Bgr Cyan = new Bgr();

                public Hsv hsvRed = new Hsv();
                public Hsv hsvBlue = new Hsv();
                public Hsv hsvGreen = new Hsv();
                public Hsv hsvYellow = new Hsv();
                public Hsv hsvPurple = new Hsv();
                public Hsv hsvCyan = new Hsv();
        }

        commonColors colorsList = new commonColors();

        private void scanSerialPorts()
        {
            string[] ports = SerialPort.GetPortNames();

            cmbPortName.Items.Clear();
            cmbPortName.Items.AddRange(ports);

            if (ports.GetLength(0) == 0)
                MessageBox.Show("No Serial Port Found!");
            else
                cmbPortName.Text = ports[ports.GetLength(0) - 1];
        }

        long map(long x, long in_min, long in_max, long out_min, long out_max)
        {
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
        }

        private void updateMotorSpeed(double speedA, double speedB)   // speeds must be normalized between -1.0 and 1.0
        {
            if (speedA > 1.0) speedA = 1.0;
            if (speedA < -1.0) speedA = -1.0;

            if (speedB > 1.0) speedB = 1.0;
            if (speedB < -1.0) speedB = -1.0;

            int intSpeedA = (int)(speedA * 255);
            int intSpeedB = (int)(speedB * 255);

            if (!serialPort1.IsOpen)
            {
                try
                {
                    serialPort1.Open();

                    byte[] cmdPacket = { 0xFF, 0, 0 };
                    cmdPacket[1] = (byte)map(intSpeedA, -255, 255, 0, 254);
                    cmdPacket[2] = (byte)map(intSpeedB, -255, 255, 0, 254);

                    serialPort1.Write(cmdPacket, 0, 3);

                    serialPort1.Close();
                }
                catch
                {

                }
            }
        }

        // jointCount:
        //   1: green
        //   2: green, blue
        //   3: green, blue, red
        //   4: green, blue, red, yellow
        private int getCoordiantes(Image<Bgr, Byte> inputImage, int jointCount)
        {
            Image<Hsv, byte> hsvImage = inputImage.Convert<Hsv, byte>();
            Image<Gray, byte> grayImage = inputImage.Convert<Gray, byte>().PyrDown().PyrUp();

            double minArea = Math.Pow((minDiameter / 2) * ratio, 2) * Math.PI;
            double maxArea = Math.Pow((maxDiameter / 2) * ratio, 2) * Math.PI;

            bool redCenterReady = false;
            bool blueCenterReady = false;
            bool greenCenterReady = false;
            bool yellowCenterReady = false;

            colorsList.hsvRed = new Hsv(178, 243, 175);
            colorsList.hsvBlue = new Hsv(100, 248, 192);
            colorsList.hsvGreen = new Hsv(72, 227, 119);
            colorsList.hsvYellow = new Hsv(25, 214, 223);

            double hueMin;
            double saturationMin;
            double valueMin;

            double hueMax;
            double saturationMax;
            double valueMax;

            #region get red range

                double hueMin2 = 0;
                double hueMax2 = 0;

                hueMin = colorsList.hsvRed.Hue - hueTolerance;
                saturationMin = colorsList.hsvRed.Satuation - saturationTolerance;
                valueMin = colorsList.hsvRed.Value - valueTolerance;

                hueMax = colorsList.hsvRed.Hue + hueTolerance;
                saturationMax = colorsList.hsvRed.Satuation + saturationTolerance;
                valueMax = colorsList.hsvRed.Value + valueTolerance;

                if (hueMin < 0)
                {
                    hueMin2 = 180 + hueMin;
                    hueMax2 = 180;

                    hueMin = 0;
                }

                if (hueMax > 180)
                {
                    hueMax2 = hueMax - 180;
                    hueMin2 = 0;

                    hueMax = 180;
                }

                if (saturationMin < 0) saturationMin = 0;
                if (saturationMax > 255) saturationMax = 255;

                if (valueMin < 0) valueMin = 0;
                if (valueMax > 255) valueMax = 255;


                Image<Gray, byte> grayRed = hsvImage.InRange(new Hsv(hueMin, saturationMin, valueMin), new Hsv(hueMax, saturationMax, valueMax));
                Image<Gray, byte> grayRed2 = hsvImage.InRange(new Hsv(hueMin2, saturationMin, valueMin), new Hsv(hueMax2, saturationMax, valueMax));

                grayRed = grayRed | grayRed2;

            #endregion

            #region get green range

                hueMin = colorsList.hsvGreen.Hue - hueTolerance;
                saturationMin = colorsList.hsvGreen.Satuation - saturationTolerance;
                valueMin = colorsList.hsvGreen.Value - valueTolerance;

                hueMax = colorsList.hsvGreen.Hue + hueTolerance;
                saturationMax = colorsList.hsvGreen.Satuation + saturationTolerance;
                valueMax = colorsList.hsvGreen.Value + valueTolerance;

                if (hueMin < 0) hueMin = 0;
                if (hueMax > 180) hueMax = 180;
               
                if (saturationMin < 0) saturationMin = 0;
                if (saturationMax > 255) saturationMax = 255;

                if (valueMin < 0) valueMin = 0;
                if (valueMax > 255) valueMax = 255;

                Image<Gray, byte> grayGreen = hsvImage.InRange(new Hsv(hueMin, saturationMin, valueMin), new Hsv(hueMax, saturationMax, valueMax));
            
            #endregion

            #region get blue range

                hueMin = colorsList.hsvBlue.Hue - hueTolerance;
                saturationMin = colorsList.hsvBlue.Satuation - saturationTolerance;
                valueMin = colorsList.hsvBlue.Value - valueTolerance;

                hueMax = colorsList.hsvBlue.Hue + hueTolerance;
                saturationMax = colorsList.hsvBlue.Satuation + saturationTolerance;
                valueMax = colorsList.hsvBlue.Value + valueTolerance;

                if (hueMin < 0) hueMin = 0;
                if (hueMax > 180) hueMax = 180;

                if (saturationMin < 0) saturationMin = 0;
                if (saturationMax > 255) saturationMax = 255;

                if (valueMin < 0) valueMin = 0;
                if (valueMax > 255) valueMax = 255;

                Image<Gray, byte> grayBlue = hsvImage.InRange(new Hsv(hueMin, saturationMin, valueMin), new Hsv(hueMax, saturationMax, valueMax));
            
            #endregion           
            
            #region get yellow range

                hueMin = colorsList.hsvYellow.Hue - hueTolerance;
                saturationMin = colorsList.hsvYellow.Satuation - saturationTolerance;
                valueMin = colorsList.hsvYellow.Value - valueTolerance;

                hueMax = colorsList.hsvYellow.Hue + hueTolerance;
                saturationMax = colorsList.hsvYellow.Satuation + saturationTolerance;
                valueMax = colorsList.hsvYellow.Value + valueTolerance;

                if (hueMin < 0) hueMin = 0;
                if (hueMax > 180) hueMax = 180;

                if (saturationMin < 0) saturationMin = 0;
                if (saturationMax > 255) saturationMax = 255;

                if (valueMin < 0) valueMin = 0;
                if (valueMax > 255) valueMax = 255;

                Image<Gray, byte> grayYellow = hsvImage.InRange(new Hsv(hueMin, saturationMin, valueMin), new Hsv(hueMax, saturationMax, valueMax));

            #endregion           
            
            grayRed = grayRed.Erode(3);
            grayGreen = grayGreen.Erode(3);
            grayBlue = grayBlue.Erode(3);
            grayYellow = grayYellow.Erode(3);

            grayRed = grayRed.Dilate(3);
            grayGreen = grayGreen.Dilate(3);
            grayBlue = grayBlue.Dilate(3);
            grayYellow = grayYellow.Dilate(3);

            BgrOrColors = inputImage.CopyBlank().Not();

            if (isFirstFrame)
            {
                #region get green color coordinates

                Contour<Point> contoursGreen = grayGreen.FindContours();

                while (contoursGreen != null)
                {
                    MCvMoments moment = contoursGreen.GetMoments();
                    float x = (float)moment.GravityCenter.x;
                    float y = (float)moment.GravityCenter.y;

                    if (contoursGreen.Area > minArea && contoursGreen.Area < maxArea && !greenCenterReady)
                    {
                        greenCenterReady = true;
                        greenCenter = new PointF(x, y);
                        BgrOrColors.Draw(new CircleF(greenCenter, maxDiameter * (float)ratio / 2), new Bgr(Color.Green), -1);
                        CircleF dot = new CircleF(greenCenter, 2);
                        BgrOrColors.Draw(dot, new Bgr(Color.White), -1);
                    }

                    contoursGreen = contoursGreen.HNext;
                }

                #endregion

                if (greenCenterReady) isFirstFrame = false;

            }
            else
            {
                greenCenterReady = true;
                BgrOrColors.Draw(new CircleF(greenCenter, maxDiameter * (float)ratio / 2), new Bgr(Color.Green), -1);
                CircleF dot = new CircleF(greenCenter, 2);
                BgrOrColors.Draw(dot, new Bgr(Color.White), -1);
            }

            #region get red color coordinates

                Contour<Point> contoursRed = grayRed.FindContours();

                while (contoursRed != null)
                {
                    MCvMoments moment = contoursRed.GetMoments();
                    float x = (float)moment.GravityCenter.x;
                    float y = (float)moment.GravityCenter.y;

                    if (contoursRed.Area > minArea && contoursRed.Area < maxArea && !redCenterReady)
                    {
                        redCenterReady = true;
                        redCenter = new PointF(x, y);                        
                        BgrOrColors.Draw(new CircleF(redCenter, maxDiameter * (float)ratio / 2), new Bgr(Color.Red), -1);
                        CircleF dot = new CircleF(redCenter, 2);
                        BgrOrColors.Draw(dot, new Bgr(Color.White), -1);
                        
                    }

                    contoursRed = contoursRed.HNext;
                }

            #endregion

            #region get blue color coordinates

                Contour<Point> contoursBlue = grayBlue.FindContours();

                while (contoursBlue != null)
                {
                    MCvMoments moment = contoursBlue.GetMoments();
                    float x = (float)moment.GravityCenter.x;
                    float y = (float)moment.GravityCenter.y;

                    if (contoursBlue.Area > minArea && contoursBlue.Area < maxArea && !blueCenterReady)
                    {
                        blueCenterReady = true;
                        blueCenter = new PointF(x, y);
                        BgrOrColors.Draw(new CircleF(blueCenter, maxDiameter * (float)ratio / 2), new Bgr(Color.Blue), -1);
                        CircleF dot = new CircleF(blueCenter, 2);
                        BgrOrColors.Draw(dot, new Bgr(Color.White), -1);
                    
                    }

                    contoursBlue = contoursBlue.HNext;
                }

            #endregion

            #region get yellow color coordinates

                Contour<Point> contoursYellow = grayYellow.FindContours();

                while (contoursYellow != null)
                {
                    MCvMoments moment = contoursYellow.GetMoments();
                    float x = (float)moment.GravityCenter.x;
                    float y = (float)moment.GravityCenter.y;

                    if (contoursYellow.Area > minArea && contoursYellow.Area < maxArea && !yellowCenterReady)
                    {
                        yellowCenterReady = true;
                        yellowCenter = new PointF(x, y);
                        BgrOrColors.Draw(new CircleF(yellowCenter, maxDiameter * (float)ratio / 2), new Bgr(Color.Yellow), -1);
                        CircleF dot = new CircleF(yellowCenter, 2);
                        BgrOrColors.Draw(dot, new Bgr(Color.White), -1);

                    }

                    contoursYellow = contoursYellow.HNext;
                }

            #endregion

            switch (jointCount)
            {
                case 1:
                    if (greenCenterReady) return 1; else return 0;
                case 2:
                    if (greenCenterReady && blueCenterReady) return 1; else return 0;
                case 3:
                    if (greenCenterReady && redCenterReady && blueCenterReady) return 1; else return 0;
                case 4:
                    if (greenCenterReady && redCenterReady && blueCenterReady && yellowCenterReady) return 1; else return 0;
                default:
                    MessageBox.Show("Invalid jointCount: Only 1,2,3,4");
                    return 0;

            }
            if (greenCenterReady && redCenterReady && blueCenterReady && yellowCenterReady) return 1; else return 0;
        }

        private void releaseCapture()
        {
            if (capture != null)
            {
                capture.Dispose();
                capture = null;
            }
        }

        private bool createCapture()
        {
            bool captureSuccessful = false;

            #region if capture is not created, create it now
            if (capture == null)
            {
                try
                {
                    captureSuccessful = true;
                    capture = new Capture(cameraIndex);                   
                }
                catch (NullReferenceException excpt)
                {
                    captureSuccessful = false;
                    MessageBox.Show(excpt.Message);
                }
            }
            #endregion

            return captureSuccessful;
        }

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (captureInProgress)
            { 
                releaseCapture();
                captureInProgress = false;
                isFirstFrame = true;
                button1.Text = "Start";
                groupBox1.Enabled = true;
                updateMotorSpeed(0, 0);
                timer1.Enabled = false;
            }
            else
            {
                if (cmbPortName.Text != "")
                {
                    if (createCapture())
                    {
                        captureInProgress = true;
                        button1.Text = "Stop";
                        serialPort1.PortName = cmbPortName.Text;
                        groupBox1.Enabled = false;
                        timer1.Interval = (int)dt;
                        timer1.Enabled = true;
                    }
                }
                else
                {
                    MessageBox.Show("No Serial Port Name Selected");
                }
            }
        }

        private void controller()
        {

            //double xd = 20;    // in centimeters
            //double x = redX;   // in centimeters

            //last_error = error;
            //error = xd - x;

            double q1 = Math.Atan2(blueY, blueX);                     // in radians
            //double q2 = Math.Atan2(redY - blueY, redX - blueX) - q1;  // in radians

            //const double l1 = 30;  // in centimeters
            //const double l2 = 30;  // in centimeters

            //const double m1 = 250;  // in grams
            //const double m2 = 250;  // in grams

            //const double d1 = 15;  // in centimeters
            //const double d2 = 15;  // in centimeters

            //const double I1 = 0.002;
            //const double I2 = 0.002;

            //double J = l1 * Math.Cos(q1) - (d2 * l1 * (l2 * m2 * Math.Cos(q1) + l2 * m2 * Math.Cos(q1 + 2 * q2))) / (2 * (m2 * Math.Pow(d2, 2) + I2));

            const double Kp = 1;
            const double Ki = 0.01;
            const double Kd = 0;

            //double T = J * (Kd * (error - last_error) / (dt / 1000) + Kp * error);

            double command = 0;

            error = command - q1 * (180 / Math.PI);

            double P = Kp * (error - error1);              // calc proportional term
            double I = Ki * (error + error1) / 2;           // integral term
            double D = Kd * (error - 2 * error1 + error1);      // derivative term 

            double drive = last + (int)(P + I + D);         // Total drive = P+I+D
            drive = (int)(drive); // scale Drive to be in the range 0-255


            if (drive < -100)
            {
                drive = -100;
            }

            if (drive > 100)
            {
                drive = 100;
            }

            updateMotorSpeed(drive / 100, 0);
            last = drive; // save current value for next time 

            error2 = error1;
            error1 = error;
        }
        private void timer1_Tick(object sender, EventArgs e)
        {
            if (capture != null)
            {
                Image<Bgr, Byte> frame = capture.QueryFrame();
                if (frame != null)
                {
                    pictureBox1.Image = frame.ToBitmap();

                    if (getCoordiantes(frame,3) == 1)
                    {
                        double K = Math.Sqrt(Math.Pow(blueCenter.X - greenCenter.X, 2) + Math.Pow(blueCenter.Y - greenCenter.Y, 2)) / 30.0;

                        redX = (1 / K) * (redCenter.X - greenCenter.X);
                        redY = - (1 / K) * (redCenter.Y - greenCenter.Y);

                        blueX = (1 / K) * (blueCenter.X - greenCenter.X);
                        blueY = - (1 / K) * (blueCenter.Y - greenCenter.Y);

                        yellowX = (1 / K) * (yellowCenter.X - greenCenter.X);
                        yellowY = - (1 / K) * (yellowCenter.Y - greenCenter.Y);

                        label1.Text = "Origin (Green): " + Math.Round(greenCenter.X, 0).ToString() + " px, " + Math.Round(greenCenter.Y, 0).ToString() + " px";
                        label2.Text = "Joint1 (Blue): " + Math.Round(blueX, 0).ToString() + " cm, " + Math.Round(blueY, 0).ToString() + " cm";
                        label3.Text = "Joint2 (Red): " + Math.Round(redX, 0).ToString() + " cm, " + Math.Round(redY, 0).ToString() + " cm";
                        label4.Text = "Joint3 (Yellow): " + Math.Round(yellowX, 0).ToString() + " cm, " + Math.Round(yellowY, 0).ToString() + " cm";

                        pictureBox2.Image = BgrOrColors.ToBitmap();

                        # region Controller Code

                        //controller();
                        updateMotorSpeed(0.2, -0.2);

                        # endregion
                    }
                }
            }          
        }

        private void button3_Click(object sender, EventArgs e)
        {
            scanSerialPorts();
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            updateMotorSpeed(0, 0);
        }
    }
}
