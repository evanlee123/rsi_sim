// We can then use the TradeKingApi class to instantiate an OAuthService and Token to make requests against the API.

// package com.tradeking;
import java.io.StringReader;

import org.w3c.dom.*;
/*
import org.scribe.builder.*;
import org.scribe.model.*;
import org.scribe.oauth.*;
import org.scribe.builder.api.DefaultApi10a;
import org.scribe.model.Token;
*/
import java.lang.Object;
import java.lang.Exception;
import javax.xml.ws.http.HTTPException;
// import org.apache.commons.lang3.StringUtils;
 
import java.util.*;
import java.text.ParseException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.TimeUnit;

import java.io.*;
import java.io.File;
import java.io.FileWriter;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.*;

import java.net.*;
import java.net.Authenticator;
import java.net.PasswordAuthentication;
import java.net.URL;
import javax.net.ssl.HttpsURLConnection;

import javax.net.ssl.HostnameVerifier;
// import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import java.security.cert.X509Certificate;
import java.security.NoSuchAlgorithmException;
import java.security.KeyManagementException;
 
import java.util.Properties;

import java.time.Instant;

// import java.sql.Timestamp;

class MyAuthenticator extends Authenticator
   {
   /**
   * Called when password authorization is needed.
   * @return The PasswordAuthentication collected from the
   * user, or null if none is provided.
   */
   protected PasswordAuthentication getPasswordAuthentication()
      {
      return new PasswordAuthentication ( "username", "password".toCharArray() );
      }
   }

public class get_data
{
	private static FileWriter logWriter = null; 
	private static String cookie;
	private static String crumb;

	public static void main(String[] args)
	{
		BufferedReader br = null;
		String oneLine;
		String htmlString;
		String cookie_filename = "yahoo_cookie.txt";
		LinkedList<String> symList = new LinkedList<String>();

		if (args.length < 3) {
			System.out.println("Usage : java get_data <date(yyyy-mm-dd)> <file_folder>");
		}

		try {
			br = new BufferedReader(new FileReader(args[0]));
			while ((oneLine = br.readLine()) != null) {
				String[] field = oneLine.split(",");
				if (field[0].length() != 0) {
					symList.add(field[0]);
				}
			}
		// } catch (FileNotFoundException e) {
		} catch (IOException e) {
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (IOException e) {
				}
			}
		}

		if (Files.exists(Paths.get(cookie_filename))) {
			try {
				br = new BufferedReader(new FileReader(cookie_filename));
				cookie = br.readLine();
				crumb = br.readLine();
			} catch (FileNotFoundException e) {
			} catch (IOException e) {
			} finally {
				if (br != null) {
					try {
						br.close();
					} catch (IOException e) {
					}
				}
			}
		} else {
			boolean bGotCrumb = GetCrumb();
			if (bGotCrumb) {
				try {
					logWriter = new FileWriter(cookie_filename);
					logWriter.append(cookie + "\n");
					logWriter.append(crumb + "\n");
					logWriter.flush();
					logWriter.close();
				} catch (IOException e) {
				}
			}
		}
		// crumb = StringUtils.stripStart(crumb, "\"");
		// crumb = StringUtils.stripEnd(crumb, "\"");
// https://query1.finance.yahoo.com/v7/finance/download/NEE?period1=1495647884&period2=1498326284&interval=1d&events=history&crumb=oBMQ0T.oLdw
		crumb = crumb.replaceAll("\"", "");
		System.out.println(cookie);
		System.out.println(crumb);
		Instant instant = Instant.parse(args[1] + "T09:30:00.00Z");
		String period1 = Long.toString(instant.getEpochSecond());
		System.out.println(period1);
		// instant = Instant.parse("2017-06-23T09:30:00.00Z");
		// String period2 = Long.toString(instant.getEpochSecond());
		String period2 = Long.toString(Instant.now().getEpochSecond());
		System.out.println(period2);
		for (int i = 1; i < symList.size(); i++) {
			String quote_link = "https://query1.finance.yahoo.com/v7/finance/download/";
			String symbol = symList.get(i);
			// if (symbol == "") break;
			System.out.println("Loading data for " + symbol + "...");
			quote_link += symbol;
			quote_link += "?period1=";
			quote_link += period1;
			quote_link += "&period2=";
			quote_link += period2;
			quote_link += "&interval=1d&events=history&crumb=";
			quote_link += crumb;
			System.out.println(quote_link);
			String[] field = cookie.split(";");
			field = field[0].split("&");
			System.out.println(field[0]);

			try {
				URL u = new URL(quote_link);
				HttpsURLConnection http = (HttpsURLConnection)u.openConnection();
				Authenticator.setDefault( new MyAuthenticator() );
				http.setAllowUserInteraction(true);
				http.setRequestMethod("GET");
				http.setRequestProperty("Cookie", cookie);
				http.connect();

				InputStream is = http.getInputStream();
				//FileOutputStream os = new FileOutputStream("..\\ggz\\" + args[2] + "\\" + symbol + ".csv");
				FileOutputStream os = new FileOutputStream(args[2] + "\\" + symbol + ".csv");
				int bytesRead = -1;
				byte[] buffer = new byte[4096];
				while ((bytesRead = is.read(buffer)) != -1) {
					os.write(buffer, 0, bytesRead);
				}
				os.close();
				is.close();
/*				BufferedReader reader = new BufferedReader(new InputStreamReader(is));
				// StringBuilder stringBuilder = new StringBuilder();
				String line = null;
				while ((line = reader.readLine()) != null) {
					System.out.println(line);
					// stringBuilder.append(line + "\n");
				} */
			} catch (HTTPException he) {
				System.out.println("Ouch - a HTTPException happened.");
				// return null;
			} catch (IOException ioe) {
				System.out.println("Oops- an IOException happened. " + ioe.getMessage());
				// return null;
			} 
		}
	}

	private static boolean GetCrumb()
	{
		boolean retValue = false;
		// Create a trust manager that does not validate certificate chains
		TrustManager[] trustAllCerts = new TrustManager[] {new X509TrustManager() {
			public java.security.cert.X509Certificate[] getAcceptedIssuers() {
				return null;
			}
			public void checkClientTrusted(X509Certificate[] certs, String authType) {
			}
			public void checkServerTrusted(X509Certificate[] certs, String authType) {
			}
		}
		};
 
		try {
			// Install the all-trusting trust manager
			SSLContext sc = SSLContext.getInstance("SSL");
			sc.init(null, trustAllCerts, new java.security.SecureRandom());
			HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
		} catch (NoSuchAlgorithmException ne) {
		} catch (KeyManagementException ke) {
		}
 
		// Create all-trusting host name verifier
		HostnameVerifier allHostsValid = new HostnameVerifier() {
			public boolean verify(String hostname, SSLSession session) {
				return true;
			}
		};
 
		// Install the all-trusting host verifier
		HttpsURLConnection.setDefaultHostnameVerifier(allHostsValid);
 
		try {
			URL u = new URL("https://finance.yahoo.com/quote/SPY/history?p=SPY");
			HttpsURLConnection http = (HttpsURLConnection)u.openConnection();
			Authenticator.setDefault( new MyAuthenticator() );
			http.setAllowUserInteraction(true);
			http.setRequestMethod("GET");
			http.connect();

			//get all headers
			/* Map<String, List<String>> map = http.getHeaderFields();
			for (Map.Entry<String, List<String>> entry : map.entrySet()) {
				System.out.println("Key : " + entry.getKey() + " ,Value : " + entry.getValue());
			} */

			cookie = http.getHeaderField("Set-Cookie");

			InputStream is = http.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(is));
			// StringBuilder stringBuilder = new StringBuilder();
			String line = null;
			while ((line = reader.readLine()) != null) {
				int pos = line.indexOf("CrumbStore");
				if (pos != -1) {
					int left = line.indexOf('{', pos);
					int right = line.indexOf('}', left);
					left = line.indexOf(':', left);
					crumb = line.substring(left + 1, right);
					retValue = true;
					break;
				}
				// System.out.println(line);
				// stringBuilder.append(line + "\n");
			}
			// return stringBuilder.toString();    
		} catch (HTTPException he) {
			System.out.println("Ouch - a HTTPException happened.");
			// return null;
		} catch (IOException ioe) {
			System.out.println("Oops- an IOException happened.");
			// return null;
		}
		return retValue;
	}

	private static String GetHtmlAndParse_s(String url)
	{
		// Create a trust manager that does not validate certificate chains
		TrustManager[] trustAllCerts = new TrustManager[] {new X509TrustManager() {
			public java.security.cert.X509Certificate[] getAcceptedIssuers() {
				return null;
			}
			public void checkClientTrusted(X509Certificate[] certs, String authType) {
			}
			public void checkServerTrusted(X509Certificate[] certs, String authType) {
			}
		}
		};
 
		try {
			// Install the all-trusting trust manager
			SSLContext sc = SSLContext.getInstance("SSL");
			sc.init(null, trustAllCerts, new java.security.SecureRandom());
			HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
		} catch (NoSuchAlgorithmException ne) {
		} catch (KeyManagementException ke) {
		}
 
		// Create all-trusting host name verifier
		HostnameVerifier allHostsValid = new HostnameVerifier() {
			public boolean verify(String hostname, SSLSession session) {
				return true;
			}
		};
 
		// Install the all-trusting host verifier
		HttpsURLConnection.setDefaultHostnameVerifier(allHostsValid);
 
		try {
			URL u = new URL(url);
			HttpsURLConnection http = (HttpsURLConnection)u.openConnection();
			Authenticator.setDefault( new MyAuthenticator() );
			http.setAllowUserInteraction(true);
			http.setRequestMethod("GET");
			http.connect();

			InputStream is = http.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(is));
			StringBuilder stringBuilder = new StringBuilder();
			String line = null;
			while ((line = reader.readLine()) != null) {
				// System.out.println(line);
				stringBuilder.append(line + "\n");
			}
			return stringBuilder.toString();    
		} catch (HTTPException he) {
			System.out.println("Ouch - a HTTPException happened.");
			return null;
		} catch (IOException ioe) {
			System.out.println("Oops- an IOException happened.");
			return null;
		}

	}

	private static String GetHtmlAndParse(String url)
	{
		URL u;
		InputStream is = null;
		DataInputStream dis;
		StringBuilder stringBuilder = new StringBuilder();
		String s;

		try {
 			u = new URL(url);
 			is = u.openStream();         // throws an IOException
 
			dis = new DataInputStream(new BufferedInputStream(is));
 
			while ((s = dis.readLine()) != null) {
				// System.out.println(s);
				stringBuilder.append(s + "\n");
			}
 
			return stringBuilder.toString();    
		} catch (MalformedURLException mue) {
 
			System.out.println("Ouch - a MalformedURLException happened.");
 			return null;

		} catch (IOException ioe) {

			System.out.println("Oops- an IOException happened.");
			return null;
 		}
	}

}

