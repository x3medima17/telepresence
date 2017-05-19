using Microsoft.Kinect;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Samples.Kinect.BodyBasics
{
    class Arm
    {
        Vector3 shoulder, elbow, wrist;

        public Arm(CameraSpacePoint shoulder, CameraSpacePoint elbow, CameraSpacePoint wrist)
        {
            this.shoulder = new Vector3(shoulder.X, shoulder.Y, shoulder.Z);
            this.elbow = new Vector3(elbow.X, elbow.Y, elbow.Z);
            this.wrist = new Vector3(wrist.X, wrist.Y, wrist.Z);
        }

        public string serialize()
        {
            string res = "{";
            res += " \"shoulder\" : " + String.Format("[{0}, {1}, {2}],", shoulder.x, shoulder.y, shoulder.z);
            res += " \"elbow\" : " + String.Format("[{0}, {1}, {2}],", elbow.x, elbow.y, elbow.z);
            res += " \"wrist\" : " + String.Format("[{0}, {1}, {2}]", wrist.x, wrist.y, wrist.z);
            res += "}";
            return res;
        }
    }
}
