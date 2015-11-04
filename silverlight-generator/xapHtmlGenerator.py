colour = ["red", "red", "green", "yellow"]

for i in range(1, 554):

    html_data = """<style type="text/css">
        html, body {
            height: 100%;
            overflow: auto;
        }
        body {
            padding: 0;
            margin: 0;
        }
        #silverlightControlHost {
            height: 100%;
            text-align:center;
        }
        </style>
        
        <script type="text/javascript">
            function onSilverlightError(sender, args) {
                var appSource = "";
                if (sender != null && sender != 0) {
                  appSource = sender.getHost().Source;
                }
                
                var errorType = args.ErrorType;
                var iErrorCode = args.ErrorCode;

                if (errorType == "ImageError" || errorType == "MediaError") {
                  return;
                }

                var errMsg = "Unhandled Error in Silverlight Application " +  appSource + "\n" ;

                errMsg += "Code: "+ iErrorCode + "    \n";
                errMsg += "Category: " + errorType + "       \n";
                errMsg += "Message: " + args.ErrorMessage + "     \n";

                if (errorType == "ParserError") {
                    errMsg += "File: " + args.xamlFile + "     \n";
                    errMsg += "Line: " + args.lineNumber + "     \n";
                    errMsg += "Position: " + args.charPosition + "     \n";
                }
                else if (errorType == "RuntimeError") {           
                    if (args.lineNumber != 0) {
                        errMsg += "Line: " + args.lineNumber + "     \n";
                        errMsg += "Position: " +  args.charPosition + "     \n";
                    }
                    errMsg += "MethodName: " + args.methodName + "     \n";
                }

                throw new Error(errMsg);
            }
        </script>"""

    xap_data_start = """    <form id="form1" runat="server" style="height:100%">
        <div id="silverlightControlHost">
            <object data="data:application/x-silverlight-2," type="application/x-silverlight-2" width="100%" height="100%">"""

    xap_data_end = """        <param name="onError" value="onSilverlightError" />
              <param name="background" value="white" />
              <param name="minRuntimeVersion" value="5.0.61118.0" />
              <param name="autoUpgrade" value="true" />
              <a href="http://go.microsoft.com/fwlink/?LinkID=149156&v=5.0.61118.0" style="text-decoration:none">
                  <img src="http://go.microsoft.com/fwlink/?LinkId=161376" alt="Get Microsoft Silverlight" style="border-style:none"/>
              </a>
            </object><iframe id="_sl_historyFrame" style="visibility:hidden;height:0px;width:0px;border:0px"></iframe></div>
        </form>"""

    with open('%s.html' % ('{0:04}'.format(i)), 'w') as myFile:
        myFile.write('<html xmlns="http://www.w3.org/1999/xhtml" >')
        myFile.write('<head>')
        myFile.write('<title>Crash Test: %s</title>' % ('{0:04}'.format(i)))
        myFile.write('<META http-equiv="refresh" content="2; URL=%s.html">' % ('{0:04}'.format(i+1)))

        myFile.write(html_data)
        myFile.write('</head>')
        myFile.write("<body>")
        myFile.write(xap_data_start)
        myFile.write('<param name="source" value="%s.xap"/>' % ('{0:04}'.format(i+1)));
        myFile.write(xap_data_end)

        myFile.write('</body>')
        myFile.write('</html>')