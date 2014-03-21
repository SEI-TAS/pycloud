package edu.cmu.sei.cloudlet.client.caching.ui;

import android.app.Activity;
import android.content.Context;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import edu.cmu.sei.ams.cloudlet.Service;
import edu.cmu.sei.cloudlet.client.CurrentCloudlet;
import edu.cmu.sei.cloudlet.client.R;
import edu.cmu.sei.cloudlet.client.ui.ConnectionInfoFragment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.ext.XLogger;
import org.slf4j.ext.XLoggerFactory;

import java.util.ArrayList;
import java.util.List;

/**
 * User: jdroot
 * Date: 3/21/14
 * Time: 10:38 AM
 */
public class ListServicesActivity extends Activity
{
    private static XLogger log = XLoggerFactory.getXLogger(ListServicesActivity.class);

    private ServiceRowAdapter adapter;
    private List<Service> serviceObjects;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.cloudlet_services_list);

        ConnectionInfoFragment connInfoFragment = (ConnectionInfoFragment) getFragmentManager().findFragmentById(R.id.connInfoPanel);
        connInfoFragment.setCloudletInfo(CurrentCloudlet.name, CurrentCloudlet.ipAddress);

        ListView listView = (ListView)findViewById(R.id.listView);
        serviceObjects = new ArrayList<Service>();
        adapter = new ServiceRowAdapter(this, R.layout.cloudlet_app_item, serviceObjects);
        listView.setAdapter(adapter);
        log.info("SERVICES ACTIVITY OPENED UP BABY");

        new GetServicesListAsync().execute();
    }


    private class ServiceRowAdapter extends ArrayAdapter<Service>
    {
        public ServiceRowAdapter(Context context, int textViewResourceId, List<Service> objects)
        {
            super(context, textViewResourceId, objects);
        }

        public View getView(int position, View convertView, ViewGroup parent)
        {
            View v = convertView;
            if( v == null )
            {
                LayoutInflater inflator = (LayoutInflater)getSystemService(LAYOUT_INFLATER_SERVICE);
                v = inflator.inflate(R.layout.cloudlet_service_item, null);
            }

            Service service = getItem(position);

            TextView idTextView = (TextView)v.findViewById(R.id.idTextView);
            TextView descriptionTextView = (TextView)v.findViewById(R.id.descriptionTextView);

            idTextView.setText(service.getServiceId());
            descriptionTextView.setText(service.getServiceId());

            return v;
        }
    }

    private class GetServicesListAsync extends AsyncTask<Void, Void, List<Service>>
    {

        private Exception e;

        @Override
        protected List<Service> doInBackground(Void... voids)
        {
            try
            {
                log.info("Running in background!");
                return CurrentCloudlet.cloudlet.getServices();
            }
            catch (Exception e)
            {
                log.info("Running in background!");
                this.e = e;
                return null;
            }
        }

        @Override
        protected void onPostExecute(List<Service> services)
        {
            if (services == null)
            {
                Toast.makeText(ListServicesActivity.this, "Error getting app list: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                return;
            }
            log.info("Got " + services.size() + " services");
            serviceObjects.clear();
            serviceObjects.addAll(services);
            adapter.notifyDataSetChanged();
        }
    }
}
