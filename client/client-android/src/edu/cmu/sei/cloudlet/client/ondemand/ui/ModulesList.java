package edu.cmu.sei.cloudlet.client.ondemand.ui;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import android.app.AlertDialog;
import android.app.ListActivity;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.BaseAdapter;
import android.widget.TextView;
import edu.cmu.sei.cloudlet.client.ondemand.models.ProvisioningModuleInfo;

/**
 * This list activity shows a list of all the provisioning modules on the SD card.
 * 
 * @author secheverria
 * 
 */
public class ModulesList extends ListActivity implements OnItemClickListener
{
    public static final String LOG_TAG = ModulesList.class.getName();
    
    // Directory on the SD Card that stores the provisioning modules folders.
    public static final String CLOUDLET_MODULES_DIR = Environment.getExternalStorageDirectory() + "/cloudlet/modules";    

    public static final int MENU_OPTION_REFRESH = 1;
    
    protected ArrayList<String> moduleFoldersList;
    protected BaseAdapter moduleFoldersAdapter;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        setTitle("Cloudlet Modules");

        loadModulesList();

        getListView().setOnItemClickListener(this);
    }

    private void loadModulesList()
    {
        // Make sure the module directory exists on the SD card.
        final File modulesFolder = new File(CLOUDLET_MODULES_DIR);        
        boolean dirExists = checkModulesFolderExistance(modulesFolder);
        if (dirExists)
        {
            moduleFoldersList = new ArrayList<String>(
                    getModuleFoldersNames(modulesFolder));

        }
        else
        {
            moduleFoldersList = new ArrayList<String>();
            moduleFoldersList.add("Module directory ["
                    + CLOUDLET_MODULES_DIR
                    + "] doesn't exist on the SD card");
        }

        moduleFoldersAdapter = new ModuleNamesListAdapter(this,
                moduleFoldersList);
        setListAdapter(moduleFoldersAdapter);
    }

    protected boolean checkModulesFolderExistance(final File modulesDir)
    {
        if (modulesDir != null && modulesDir.exists())
        {
            Log.i(LOG_TAG, "Modules directory " + modulesDir.getAbsolutePath()
                    + " exists.");
            return true;
        }
        else
        {
            // Create the required folders if missing.
            Log.i(LOG_TAG, "The cloudlet modules file directory doesn't exist "
                    + CLOUDLET_MODULES_DIR
                    + " exists; creating it.");
            modulesDir.mkdirs();

            // If we weren't able to create the folder, just notify the user.
            if (!modulesDir.exists())
            {
                AlertDialog.Builder builder = new AlertDialog.Builder(this);
                builder.setTitle("Modules Directory Does not Exist");
                final TextView message = new TextView(this);
                message.setText("The directory " + modulesDir.getAbsolutePath()
                        + " doesn't exist and could not be created.");
                builder.setView(message);
                builder.setPositiveButton("Done",
                        new DialogInterface.OnClickListener()
                        {
                            @Override
                            public void onClick(DialogInterface dialog,
                                    int which)
                            {
                            }
                        });

                builder.create().show();
                return false;
            }
            else
            {
                return true;
            }
        }
    }

    protected List<String> getModuleFoldersNames(File modulesDir)
    {
        List<String> list = new ArrayList<String>();

        // Get all the subdirectories of the modules dir.
        File[] subfolderList = modulesDir.listFiles();
        if (subfolderList == null || subfolderList.length == 0)
        {
            list.add("Modules directory ["
                    + CLOUDLET_MODULES_DIR
                    + "] doesn't contain any module folders.");
            return list;
        }
        else
        {
            for (File folder : subfolderList)
            {
                if(folder.isDirectory())
                {
                    // Check if it actually contains an module.
                    try
                    {
                        // This is called to validate if it is a valid module.
                        ProvisioningModuleInfo moduleInfo = new ProvisioningModuleInfo(folder.getAbsolutePath());
                        
                        // If we are ok, we add it to the list.
                        list.add(folder.getName());
                    }
                    catch(RuntimeException e)
                    {
                        Log.w(LOG_TAG, "Ignoring folder with no valid module: " + folder.getName());
                    }                    
                }
            }
        }

        return list;
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        super.onPrepareOptionsMenu(menu);
        menu.add(0, MENU_OPTION_REFRESH, 0, "Refresh");
        return true;
    }

    @Override
    public boolean onMenuItemSelected(int featureId, MenuItem item)
    {
        switch (item.getItemId())
        {
            case MENU_OPTION_REFRESH:
                loadModulesList();
                break;
        }
        return true;

    }

    @Override
    public void onItemClick(final AdapterView<?> arg0, View arg1,
            final int itemclicked, long arg3)
    {

        String clickedFolderName = (String) this.moduleFoldersAdapter
                .getItem(itemclicked);

        if (clickedFolderName != null)
        {
            
            Intent intent = new Intent(this, ODProvisioningActivity.class);
            intent.putExtra(ODProvisioningActivity.INTENT_EXTRA_BASE_MODULES_FOLDER,
                    CLOUDLET_MODULES_DIR);
            intent.putExtra(ODProvisioningActivity.INTENT_EXTRA_USER_SELECTED_MODULE_FOLDER,
                            clickedFolderName);
            startActivity(intent);
        }
    }

}

class ModuleNamesListAdapter extends BaseAdapter
{

    private List<String> fileNames;
    private Context context;

    public ModuleNamesListAdapter(final Context ctx,
            final List<String> infileNames)
    {
        fileNames = infileNames;
        context = ctx;

    }

    @Override
    public int getCount()
    {
        return fileNames.size();
    }

    @Override
    public Object getItem(int position)
    {
        return fileNames.get(position);
    }

    @Override
    public long getItemId(int position)
    {
        return position;
    }

    @Override
    public void notifyDataSetChanged()
    {
        super.notifyDataSetChanged();
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent)
    {

        View v = convertView;
        TextView tv;

        if (v == null)
            tv = new TextView(context);
        else
            tv = ((TextView) convertView);

        tv.setText(fileNames.get(position));
        tv.setPadding(15, 10, 15, 10);
        tv.setTextSize(15);

        return tv;

    }

}
