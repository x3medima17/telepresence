using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Samples.Kinect.BodyBasics
{
    class DataSet
    {
        Arm left, right;
        public DataSet(Arm left, Arm right)
        {
            this.left = left;
            this.right = right;
        }
         public string serialize()
        {
            string res = "{";
            res += "\"left\" :"  + left.serialize() + ",";
            res += "\"right\" :" + right.serialize();
            res += "}";

            return res;
        }
    }
}
