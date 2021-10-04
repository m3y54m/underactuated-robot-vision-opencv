using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

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
        Image<Bgr, Byte> frame;
        bool captureInProgress;

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

        private void ProcessFrame(object sender, EventArgs arg)
        {
            Image<Bgr, Byte> imgCam = capture.QueryFrame();

            Image<Hsv, byte> imgHsv = imgCam.Convert<Hsv, byte>();
            Image<Gray, byte> imgGray = imgCam.Convert<Gray, byte>().PyrDown().PyrUp();


            byte saturationMin = 90;
            byte valueMin = 70;
            byte saturationMax = 230;
            byte valueMax = 170;
            int ImageSize = 550;
            int FieldRealSize = 500;
            double dif = 10;
            double k = (double)ImageSize / FieldRealSize;
            double minArea = Math.Pow(10 * k, 2) * Math.PI;
            double maxArea = Math.Pow(350 * k, 2);

            Image<Gray, byte> grayRed;
            Image<Gray, byte> grayRed2;

            colorsList.hsvRed = new Hsv(176, 140, 125);
            colorsList.hsvBlue = new Hsv(113, 185, 100);
            colorsList.hsvGreen = new Hsv(57, 140, 110);

            if (colorsList.hsvRed.Hue < 90)
            {
                grayRed = imgHsv.InRange(new Hsv(colorsList.hsvRed.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvRed.Hue + dif, saturationMax, valueMax));
                grayRed2 = imgHsv.InRange(new Hsv(180 - dif, saturationMin, valueMin), new Hsv(180, saturationMax, valueMax));
            }
            else
            {
                grayRed = imgHsv.InRange(new Hsv(colorsList.hsvRed.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvRed.Hue + dif, saturationMax, valueMax));
                grayRed2 = imgHsv.InRange(new Hsv(0, saturationMin, valueMin), new Hsv(dif, saturationMax, valueMax));
            }

            grayRed = grayRed | grayRed2;

            Image<Gray, byte> grayBlue = imgHsv.InRange(new Hsv(colorsList.hsvBlue.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvBlue.Hue + dif, saturationMax, valueMax));
            Image<Gray, byte> grayGreen = imgHsv.InRange(new Hsv(colorsList.hsvGreen.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvGreen.Hue + dif, saturationMax, valueMax));

            grayRed = grayRed.Erode(3);
            grayBlue = grayBlue.Erode(3);
            grayGreen = grayGreen.Erode(3);

            grayRed = grayRed.Dilate(3);
            grayBlue = grayBlue.Dilate(3);
            grayGreen = grayGreen.Dilate(3);

            PointF redCenter = new PointF(0, 0);
            PointF blueCenter = new PointF(0, 0);
            PointF greenCenter = new PointF(0, 0);

            Image<Bgr, byte> BgrOrColors = imgCam.CopyBlank();

            //--------------------------------------------------------------//
            Contour<Point> contoursRed = grayRed.FindContours();

            while (contoursRed != null)
            {
                MCvMoments moment = contoursRed.GetMoments();
                float x = (float)moment.GravityCenter.x;
                float y = (float)moment.GravityCenter.y;

                redCenter = new PointF(x, y);

                if (contoursRed.Area > 0.8 * minArea)
                {
                    BgrOrColors.Draw(contoursRed, new Bgr(Color.Red), -1);
                    //label1.Text = label1.Text + Convert.ToString(contoursRed.Area) + ",";
                    CircleF dot = new CircleF(new PointF(x, y), 2);
                    BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
                }

                contoursRed = contoursRed.HNext;
            }
            //--------------------------------------------------------------//

            //--------------------------------------------------------------//
            Contour<Point> contoursBlue = grayBlue.FindContours();

            while (contoursBlue != null)
            {
                MCvMoments moment = contoursBlue.GetMoments();
                float x = (float)moment.GravityCenter.x;
                float y = (float)moment.GravityCenter.y;

                blueCenter = new PointF(x, y);

                if (contoursBlue.Area > 0.8 * minArea)
                {
                    BgrOrColors.Draw(contoursBlue, new Bgr(Color.Blue), -1);
                    //label1.Text = label1.Text + Convert.ToString(contoursBlue.Area) + ",";
                    CircleF dot = new CircleF(new PointF(x, y), 2);
                    BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
                    BgrOrColors.Draw(new LineSegment2DF(redCenter, blueCenter), new Bgr(Color.Yellow), 3);
                }

                contoursBlue = contoursBlue.HNext;
            }
            //--------------------------------------------------------------//

            //--------------------------------------------------------------//
            Contour<Point> contoursGreen = grayGreen.FindContours();

            while (contoursGreen != null)
            {
                MCvMoments moment = contoursGreen.GetMoments();
                float x = (float)moment.GravityCenter.x;
                float y = (float)moment.GravityCenter.y;

                greenCenter = new PointF(x, y);

                if (contoursGreen.Area > 0.8 * minArea)
                {
                    BgrOrColors.Draw(contoursGreen, new Bgr(Color.Green), -1);
                    //label1.Text = label1.Text + Convert.ToString(contoursGreen.Area);
                    CircleF dot = new CircleF(new PointF(x, y), 2);
                    BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
                    BgrOrColors.Draw(new LineSegment2DF(greenCenter, blueCenter), new Bgr(Color.Yellow), 3);
                }

                contoursGreen = contoursGreen.HNext;
            }
            double m = Math.Sqrt(Math.Pow(blueCenter.X - greenCenter.X, 2) + Math.Pow(blueCenter.Y - greenCenter.Y, 2));
            label1.Text = "Distance: " + Math.Round(((300.0 / m) * Math.Sqrt(Math.Pow(redCenter.X - greenCenter.X, 2) + Math.Pow(redCenter.Y - greenCenter.Y, 2))), 0).ToString() + " mm";
            pictureBox1.Image = imgCam.ToBitmap();
            pictureBox2.Image = BgrOrColors.ToBitmap();
        }

        private void ReleaseData()
        {
            if (capture != null)
                capture.Dispose();
        }

        public Form1()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            // rtsp://admin:ozrais4me@192.168.0.20:554/live1.sdp // works in VLC   // not so bad
            // http://admin:ozrais4me@192.168.0.20:80/video1.mjpg  // bad
            // http://admin:ozrais4me@192.168.0.20/dms?nowprofileid=1 //JPEG  //bad
            // http://admin:ozrais4me@192.168.0.20/image/jpeg.cgi //JPEG  //bad
            // http://admin:ozrais4me@172.18.17.94/dms.jpg //JPEG
            // http://admin:ozrais4me@192.168.0.20/ipcam/stream.cgi?nowprofileid=2 //	MJPEG    // good

            string inputStream = "source/DCS-2130_201512141729534.avi";

            #region if capture is not created, create it now
            if (capture == null)
            {
                try
                {
                    capture = new Capture(0);
                    timer1.Enabled = true;
                }
                catch (NullReferenceException excpt)
                {
                    MessageBox.Show(excpt.Message);
                }
            }
            #endregion

            //if (capture != null)
            //{
            //    if (captureInProgress)
            //    {  //if camera is getting frames then stop the capture and set button Text
            //        // "Start" for resuming capture
            //        button1.Text = "Start"; //
            //        Application.Idle -= ProcessFrame;
            //    }
            //    else
            //    {
            //        //if camera is NOT getting frames then start the capture and set button
            //        // Text to "Stop" for pausing capture
            //        button1.Text = "Stop";
            //        Application.Idle += ProcessFrame;
            //    }

            //    captureInProgress = !captureInProgress;
            //}

            

            //Image<Bgr, Byte> imgCam = new Image<Bgr, byte>("source\\DCS-2130_201512141726482.jpg");

            //Image<Hsv, byte> imgHsv = imgCam.Convert<Hsv, byte>();
            //Image<Gray, byte> imgGray = imgCam.Convert<Gray, byte>().PyrDown().PyrUp();


            //byte saturationMin = 90;
            //byte valueMin = 70;
            //byte saturationMax = 230;
            //byte valueMax = 170;
            //int ImageSize = 550;
            //int FieldRealSize = 1000;
            //double dif = 10;
            //double k = (double)ImageSize / FieldRealSize;
            //double minArea = Math.Pow(10 * k, 2) * Math.PI;
            //double maxArea = Math.Pow(350 * k, 2);

            //Image<Gray, byte> grayRed;
            //Image<Gray, byte> grayRed2;

            //colorsList.hsvRed = new Hsv(176, 140, 125);
            //colorsList.hsvBlue = new Hsv(113, 185, 100);
            //colorsList.hsvGreen = new Hsv(57, 140, 110);

            //if (colorsList.hsvRed.Hue < 90)
            //{
            //    grayRed = imgHsv.InRange(new Hsv(colorsList.hsvRed.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvRed.Hue + dif, saturationMax, valueMax));
            //    grayRed2 = imgHsv.InRange(new Hsv(180 - dif, saturationMin, valueMin), new Hsv(180, saturationMax, valueMax));
            //}
            //else
            //{
            //    grayRed = imgHsv.InRange(new Hsv(colorsList.hsvRed.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvRed.Hue + dif, saturationMax, valueMax));
            //    grayRed2 = imgHsv.InRange(new Hsv(0, saturationMin, valueMin), new Hsv(dif, saturationMax, valueMax));
            //}

            //grayRed = grayRed | grayRed2;

            //Image<Gray, byte> grayBlue = imgHsv.InRange(new Hsv(colorsList.hsvBlue.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvBlue.Hue + dif, saturationMax, valueMax));
            //Image<Gray, byte> grayGreen = imgHsv.InRange(new Hsv(colorsList.hsvGreen.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvGreen.Hue + dif, saturationMax, valueMax));
            
            //grayRed = grayRed.Erode(3);
            //grayBlue = grayBlue.Erode(3);
            //grayGreen = grayGreen.Erode(3);

            //PointF redCenter = new PointF(0, 0);
            //PointF blueCenter = new PointF(0, 0);
            //PointF greenCenter = new PointF(0, 0);

            //Image<Bgr, byte> BgrOrColors = imgCam.CopyBlank();

            ////--------------------------------------------------------------//
            //Contour<Point> contoursRed = grayRed.FindContours();

            //while (contoursRed != null)
            //{
            //    MCvMoments moment = contoursRed.GetMoments();
            //    float x = (float)moment.GravityCenter.x;
            //    float y = (float)moment.GravityCenter.y;

            //    redCenter = new PointF(x,y);

            //    if (contoursRed.Area > 0.8 * minArea)
            //    {
            //        BgrOrColors.Draw(contoursRed, new Bgr(Color.Red), -1);
            //        //label1.Text = label1.Text + Convert.ToString(contoursRed.Area) + ",";
            //        CircleF dot = new CircleF(new PointF(x, y), 2);
            //        BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
            //    }

            //    contoursRed = contoursRed.HNext;
            //}
            ////--------------------------------------------------------------//

            ////--------------------------------------------------------------//
            //Contour<Point> contoursBlue = grayBlue.FindContours();

            //while (contoursBlue != null)
            //{
            //    MCvMoments moment = contoursBlue.GetMoments();
            //    float x = (float)moment.GravityCenter.x;
            //    float y = (float)moment.GravityCenter.y;

            //    blueCenter = new PointF(x,y);

            //    if (contoursBlue.Area > 0.8 * minArea)
            //    {
            //        BgrOrColors.Draw(contoursBlue, new Bgr(Color.Blue), -1);
            //        //label1.Text = label1.Text + Convert.ToString(contoursBlue.Area) + ",";
            //        CircleF dot = new CircleF(new PointF(x, y), 2);
            //        BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
            //        BgrOrColors.Draw(new LineSegment2DF(redCenter, blueCenter), new Bgr(Color.Yellow), 3);
            //    }

            //    contoursBlue = contoursBlue.HNext;
            //}
            ////--------------------------------------------------------------//

            ////--------------------------------------------------------------//
            //Contour<Point> contoursGreen = grayGreen.FindContours();

            //while (contoursGreen != null)
            //{
            //    MCvMoments moment = contoursGreen.GetMoments();
            //    float x = (float)moment.GravityCenter.x;
            //    float y = (float)moment.GravityCenter.y;

            //    greenCenter = new PointF(x,y);

            //    if (contoursGreen.Area > 0.8 * minArea)
            //    {
            //        BgrOrColors.Draw(contoursGreen, new Bgr(Color.Green), -1);
            //        //label1.Text = label1.Text + Convert.ToString(contoursGreen.Area);
            //        CircleF dot = new CircleF(new PointF(x, y), 2);
            //        BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
            //        BgrOrColors.Draw(new LineSegment2DF(greenCenter, blueCenter), new Bgr(Color.Yellow), 3);
            //    }

            //    contoursGreen = contoursGreen.HNext;
            //}
            //double m = Math.Sqrt(Math.Pow(blueCenter.X - greenCenter.X, 2) + Math.Pow(blueCenter.Y - greenCenter.Y, 2));
            //label1.Text = "Distance: " + Math.Round(((300.0 / m) * Math.Sqrt(Math.Pow(redCenter.X - greenCenter.X, 2) + Math.Pow(redCenter.Y - greenCenter.Y, 2))), 0).ToString() + " mm";
            //pictureBox1.Image = imgCam.ToBitmap();
            //pictureBox2.Image = BgrOrColors.ToBitmap();
            
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            //string localFilename = "tofile.jpg";
            //using (WebClient client = new WebClient())
            //{
            //    client.DownloadFile("http://admin:ozrais4me@172.18.17.94/dms.jpg", localFilename);
            //}
        
            Image<Bgr, Byte> imgCam = capture.QueryFrame();

            Image<Hsv, byte> imgHsv = imgCam.Convert<Hsv, byte>();
            Image<Gray, byte> imgGray = imgCam.Convert<Gray, byte>().PyrDown().PyrUp();


            byte saturationMin = 150;
            byte valueMin = 70;
            byte saturationMax = 255;
            byte valueMax = 190;
            int ImageWidth = 640;
            int FieldRealSize = 1000;
            double dif = 10;
            double k = (double)ImageWidth / FieldRealSize;
            double minArea = Math.Pow(10 * k, 2) * Math.PI;
            double maxArea = Math.Pow(350 * k, 2);

            Image<Gray, byte> grayRed;
            Image<Gray, byte> grayRed2;

            colorsList.hsvRed = new Hsv(178, 239, 148);
            colorsList.hsvBlue = new Hsv(116, 252, 109);
            colorsList.hsvGreen = new Hsv(60, 234, 133);

            if (colorsList.hsvRed.Hue < 90)
            {
                grayRed = imgHsv.InRange(new Hsv(colorsList.hsvRed.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvRed.Hue + dif, saturationMax, valueMax));
                grayRed2 = imgHsv.InRange(new Hsv(180 - dif, saturationMin, valueMin), new Hsv(180, saturationMax, valueMax));
            }
            else
            {
                grayRed = imgHsv.InRange(new Hsv(colorsList.hsvRed.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvRed.Hue + dif, saturationMax, valueMax));
                grayRed2 = imgHsv.InRange(new Hsv(0, saturationMin, valueMin), new Hsv(dif, saturationMax, valueMax));
            }

            grayRed = grayRed | grayRed2;

            Image<Gray, byte> grayBlue = imgHsv.InRange(new Hsv(colorsList.hsvBlue.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvBlue.Hue + dif, saturationMax, valueMax));
            Image<Gray, byte> grayGreen = imgHsv.InRange(new Hsv(colorsList.hsvGreen.Hue - dif, saturationMin, valueMin), new Hsv(colorsList.hsvGreen.Hue + dif, saturationMax, valueMax));

            grayRed = grayRed.Erode(2);
            grayBlue = grayBlue.Erode(2);
            grayGreen = grayGreen.Erode(2);

            grayRed = grayRed.Dilate(2);
            grayBlue = grayBlue.Dilate(2);
            grayGreen = grayGreen.Dilate(2);

            PointF redCenter = new PointF(0, 0);
            PointF blueCenter = new PointF(0, 0);
            PointF greenCenter = new PointF(0, 0);

            Image<Bgr, byte> BgrOrColors = imgCam.CopyBlank();

            //--------------------------------------------------------------//
            Contour<Point> contoursRed = grayRed.FindContours();

            while (contoursRed != null)
            {
                MCvMoments moment = contoursRed.GetMoments();
                float x = (float)moment.GravityCenter.x;
                float y = (float)moment.GravityCenter.y;

                redCenter = new PointF(x, y);

                if (contoursRed.Area > 0.8 * minArea)
                {
                    BgrOrColors.Draw(contoursRed, new Bgr(Color.Red), -1);
                    //label1.Text = label1.Text + Convert.ToString(contoursRed.Area) + ",";
                    CircleF dot = new CircleF(new PointF(x, y), 2);
                    BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
                }

                contoursRed = contoursRed.HNext;
            }
            //--------------------------------------------------------------//

            //--------------------------------------------------------------//
            Contour<Point> contoursBlue = grayBlue.FindContours();

            while (contoursBlue != null)
            {
                MCvMoments moment = contoursBlue.GetMoments();
                float x = (float)moment.GravityCenter.x;
                float y = (float)moment.GravityCenter.y;

                blueCenter = new PointF(x, y);

                if (contoursBlue.Area > 0.8 * minArea)
                {
                    BgrOrColors.Draw(contoursBlue, new Bgr(Color.Blue), -1);
                    //label1.Text = label1.Text + Convert.ToString(contoursBlue.Area) + ",";
                    CircleF dot = new CircleF(new PointF(x, y), 2);
                    BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
                    BgrOrColors.Draw(new LineSegment2DF(redCenter, blueCenter), new Bgr(Color.Yellow), 3);
                }

                contoursBlue = contoursBlue.HNext;
            }
            //--------------------------------------------------------------//

            //--------------------------------------------------------------//
            Contour<Point> contoursGreen = grayGreen.FindContours();

            while (contoursGreen != null)
            {
                MCvMoments moment = contoursGreen.GetMoments();
                float x = (float)moment.GravityCenter.x;
                float y = (float)moment.GravityCenter.y;

                greenCenter = new PointF(x, y);

                if (contoursGreen.Area > 0.8 * minArea)
                {
                    BgrOrColors.Draw(contoursGreen, new Bgr(Color.Green), -1);
                    //label1.Text = label1.Text + Convert.ToString(contoursGreen.Area);
                    CircleF dot = new CircleF(new PointF(x, y), 2);
                    BgrOrColors.Draw(dot, new Bgr(Color.Black), -1);
                    BgrOrColors.Draw(new LineSegment2DF(greenCenter, blueCenter), new Bgr(Color.Yellow), 3);
                }

                contoursGreen = contoursGreen.HNext;
            }
            double m = Math.Sqrt(Math.Pow(blueCenter.X - greenCenter.X, 2) + Math.Pow(blueCenter.Y - greenCenter.Y, 2));
            label1.Text = "Distance: " + Math.Round(((30.0 / m) * Math.Sqrt(Math.Pow(redCenter.X - greenCenter.X, 2) + Math.Pow(redCenter.Y - greenCenter.Y, 2))), 0).ToString() + " cm";
            label2.Text = greenCenter.X.ToString() + "," + greenCenter.Y.ToString();
            pictureBox1.Image = imgCam.ToBitmap();
            pictureBox2.Image = BgrOrColors.ToBitmap();
        }
    }
}
