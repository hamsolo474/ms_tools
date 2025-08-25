# ms_tools
Tools for processing Microsoft Power BI in the command line

## gjp.py Grep Json Parser

Grep Json Parser is a program to read the often malformed oneliner json that appears in many Power BI logs, such as Mashup logs from the gateway and Power BI Desktop traces.
You use it by piping information into it from GREP or some other program. For example, if you are looking for the most recent error in a Power BI Desktop trace you could do something like this
```
> cd to/the/folder/with/the/trace
> grep -rni "exception" | gjp.py Start Action | grep -i "exception"
2025-07-31T06:33:21.1004653Z    MainForm/ctor/Initialize main form's exceptionHandler
2025-07-31T06:34:56.5111840Z    WebView2BrowserWrapper(reportView.html)/OnWebViewProcessFailed Exception:Microsoft.PowerBI.Client.Windows.WebView2.WebView2ProcessCrashException: WebView2 Process Failed: ReportView, Source:https://ms-pbi.pbi.microsoft.com/minerva/reportView.html ExitCode:-536870904 Reason:OutOfMemory ProcessFailedKind:RenderProcessExited ProcessDescription:\r\n   at Microsoft.PowerBI.Client.Windows.WebView2.WebView2BrowserWrapper.OnWebViewProcessFailed(Object sender, CoreWebView2ProcessFailedEventArgs args)
```
and you will see that in this case it only returned the two exceptions which appeared in the trace i ran it on.
This is better than trying to read through all the text files manually




```gjp.py --help
usage: gjp.py [-h] [--keys] [--space] [--not-strict] [--delimeter DELIMETER] [--print-headers] [fields ...]

Read the MS malformed JSON in logs Usage example:
C:\Users\v-micgilmore\Documents\Customer\2507230030005039\PBIDesktopDiagnosticInfo.20250724T144038>grep -rni
"incident" | grep -i "category" | grep "DAXQuery" | grep DataMashup | gjp.py message

positional arguments:
  fields                json fields to look for

options:
  -h, --help            show this help message and exit
  --keys                print keys
  --space               put newline between results
  --not-strict          only print lines with all values present
  --delimeter DELIMETER
                        which delimiter to use tab, comma, colon etc..
  --print-headers       Print headers
```

## is_microsoft_ip.py

Pipe in a newline separated ips from another program like tshark and then this program can tell you if they are microsoft related IPs by looking them up in the Public Service Tags json released by Microsoft
example usage would be

```
tshark -r WIRESHARK_PCAP_FILE -Y "WIRESHARK DISPLAY FILTERS GO HERE" -T fields -e ip.dst | sort | uniq | is_microsoft.ip.py --wireshark
20.40.187.183
52.108.40.15
52.109.112.0
52.109.112.239
52.111.224.11
52.111.224.32
52.113.90.210
52.115.98.102
52.115.98.172
52.115.98.192
52.115.98.93
52.123.160.223
52.123.161.42
52.123.164.130
52.123.168.137
ip.dst == 20.40.187.183 || ip.dst == 52.108.40.15 || ip.dst == 52.109.112.0 || ip.dst == 52.109.112.239 || ip.dst == 52.111.224.11 || ip.dst == 52.111.224.32 || ip.dst == 52.113.90.210 || ip.dst == 52.115.98.102 || ip.dst == 52.115.98.172 || ip.dst == 52.115.98.192 || ip.dst == 52.115.98.93 || ip.dst == 52.123.160.223 || ip.dst == 52.123.161.42 || ip.dst == 52.123.164.130 || ip.dst == 52.123.168.137
```
This will output only the list of Microsoft IPs in the data sent to it by tshark and then a wireshark display filter you can use in wireshark gui to continue troubleshooting


```
usage: is_microsoft_ip.py [-h] [--mode {match,notmatch}] [--print-errors] [--wireshark]

Get list of IPs from stdin and check to see if they are MS

options:
  -h, --help            show this help message and exit
  --mode {match,notmatch}
                        return matching ips or non matching ips (default: match)
  --print-errors        print errors
  --wireshark           print wireshark display filter
```

## tf.py Time Filter

```
usage: tf.py [-h] [--delimeter DELIMETER] [--field FIELD] [--start START] [--end END] [--duration DURATION] [--sort SORT]

Timefilter Read PowerBI logs and only display the lines within a time range
example usage
C:\\Users\\v-micgilmore\\Documents\\Customer\\2xxxxxxxxxxxxxx6\\3Oct2024TLS13PBIDesktopDiagnosticInfo20250819T155154>grep -rni "Start" | gjp.py Start Action | tf.py --before 2025-08-19T05:11:01.0230237Z --duration 1m

options:
  -h, --help            show this help message and exit
  --delimeter DELIMETER
                        which delimeter to use tab, comma, colon etc..
  --field FIELD         which column contains the timestamp, 1 indexed
  --start START, --after START
                        Show logs after this time 2025-08-19T05:09:03.1294141Z
  --end END, --before END
                        Show logs before this time 2025-08-19T05:10:03.1294141Z
  --duration DURATION   Show logs within duration of specified time you must specify the time like this, 1h 1m 1s, you cannot do 1m30s but you can do 90s
  --sort SORT           Sort lines
```

Example:
See we are showing all the events that match our grep filter between those two times
```
>grep -rni "exception" | gjp.py Start Action | tf.py --before 2025-08-19T05:11:01.0230237Z --duration 3m
Checking between 2025-08-19 05:08:01.023023+00:00 and 2025-08-19 05:11:01.023023+00:00, 3m
2025-08-19T05:09:03.1294141Z    MainForm/ctor/Initialize main form's exceptionHandler
2025-08-19T05:09:03.2755543Z    PBI.TraceMessage
2025-08-19T05:09:03.8512142Z    PBI.PQ.SignInInternalAsync
2025-08-19T05:09:07.9296778Z    PBI.MainWindow/ctor/Create exception handler
2025-08-19T05:09:09.2117913Z    PBI.PQ.AcquirePlatformEmail
2025-08-19T05:09:14.9325339Z    PBI.PQ.SignInInternalAsync
2025-08-19T05:09:16.9725961Z    PBI.PQ.SignInInternalAsync
2025-08-19T05:09:30.1341557Z    PackagePartitionAnalysisInfo/SetPreviewValue
2025-08-19T05:11:01.0230237Z    NavigatorDialogClosed
```

## top.py
```
usage: top.py [-h] [--bottom] [--sort] quantity

Top: display the first few or last few lines from a pipe

positional arguments:
  quantity    number of lines

options:
  -h, --help  show this help message and exit
  --bottom    Return bottom rows
  --sort      Sort lines
```

See this example, without using top.py it returns hundreds of lines, but with top we can easily read the important information without having to scroll
```
>grep -rni "exception" | gjp.py Action NonFatalError --unique-count | top.py 5
763     FileSystemAccessHelper/TryIgnoringAccessExceptions      Could not find a part of the path 'C:\Windows\SystemTemp\Microsoft\MashupProvider\Temp'.
2       FileSystemAccessHelper/TryIgnoringAccessExceptions      Could not find file 'C:\Windows\SystemTemp\Microsoft\MashupProvider\Cache\85f3b009-f7d3-4ef2-9acb-b11bb260e17a\9aa299a5-dd26-4f2c-af28-ee0c25c707ad.dat'.
2       FileSystemAccessHelper/TryIgnoringAccessExceptions      Could not find file 'C:\Windows\SystemTemp\Microsoft\MashupProvider\Cache\85f3b009-f7d3-4ef2-9acb-b11bb260e17a\529849e0-38b4-4672-adad-7bbfabec4ada.dat'.
2       FileSystemAccessHelper/TryIgnoringAccessExceptions      Could not find file 'C:\Windows\SystemTemp\Microsoft\MashupProvider\Cache\52ec8b1f-1d36-4f8c-b797-7633bdf51b21\c661e1d8-7a3b-4fe9-85a7-46b4fd7c90a0.dat'.
1       FileSystemAccessHelper/TryIgnoringAccessExceptions      Could not find file 'C:\Windows\SystemTemp\Microsoft\MashupProvider\Cache\7e9e97fc-a181-493a-b6ae-00b049556446\Cache.Version'.
```
