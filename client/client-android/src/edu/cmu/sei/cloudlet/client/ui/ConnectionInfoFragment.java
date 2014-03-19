package edu.cmu.sei.cloudlet.client.ui;

import edu.cmu.sei.cloudlet.client.R;
import android.app.Fragment;
import android.content.Context;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

/**
 * Displays information about the current connection and status.
 * @author secheverria
 *
 */
public class ConnectionInfoFragment extends Fragment
{
    // Used to identify logging statements.
    private static final String LOG_TAG = ConnectionInfoFragment.class.getName();
    
    // Wi-Fi connection info.
    private TextView wifiSsidText;       
    private TextView wifiIpText;    
    private String wifiSsid;
    private String wifiIpAddress;
    
    // Selected cloudlet info.
    private TextView cloudletNameText;       
    private TextView cloudletIpText;
    
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) 
    {
        // Inflate the layout for this fragment.        
        View inflatedView = inflater.inflate(R.layout.connection_info, container, false);
        
        // Wi-Fi info.
        wifiSsidText = (TextView) inflatedView.findViewById(R.id.wifiSsid);       
        wifiIpText = (TextView) inflatedView.findViewById(R.id.wifiIp);
        updateWifiInfo();
        
        // Cloudlet info.
        cloudletNameText = (TextView) inflatedView.findViewById(R.id.cloudlet);
        cloudletIpText = (TextView) inflatedView.findViewById(R.id.cloudletIp);
        
        return inflatedView;
    }
    
    public void onResume() 
    {
        super.onResume();
        Log.d(LOG_TAG, "onResume");
        
        updateWifiInfo();
    }
    
    public void onWindowFocusChanged (boolean hasFocus)
    {
        if(hasFocus)
        {
            updateWifiInfo();
        }
    }    
    
    /**
     * Loads the SSID of the Wi-Fi network we are currently connected to, as well as the IP address
     * associated to that connection.
     */
    public void updateWifiInfo() 
    {
        WifiManager wifiManager = (WifiManager) getActivity().getSystemService(Context.WIFI_SERVICE);
        WifiInfo info = wifiManager.getConnectionInfo();
        
        if(info == null)
        {
            Log.w(LOG_TAG, "Not connected to Wi-Fi.");
            wifiSsid = "disconnected";
            wifiIpAddress = "disconnected";
            return;
        }

        wifiSsid = info.getSSID();
        int ipAddress = info.getIpAddress();
        
        String ip = null;
        ip = String.format("%d.%d.%d.%d",
                            (ipAddress & 0xff),
                            (ipAddress >> 8 & 0xff),
                            (ipAddress >> 16 & 0xff),
                            (ipAddress >> 24 & 0xff));
        
        wifiIpAddress = ip;
        
        // Update the UI.
        refreshWifiUIText();
    }
    
    
    /**
     * Refreshes the GUI to show the current information about the Wi-Fi connection.
     */
    private void refreshWifiUIText()
    {
        wifiSsidText.setText(wifiSsid);
        wifiIpText.setText(wifiIpAddress);
    }
    
    /**
     * Refreshes the GUI to show the current information about the Wi-Fi connection.
     */
    public void setCloudletInfo(String cloudletName, String cloudletIp)
    {
        cloudletNameText.setText(cloudletName);
        cloudletIpText.setText(cloudletIp);
    }     
    
    /**
     * Returns the Wi-Fi IP address.
     * @return
     */
    public String getWifiIpAddress()
    {
        return wifiIpAddress;
    }
}
