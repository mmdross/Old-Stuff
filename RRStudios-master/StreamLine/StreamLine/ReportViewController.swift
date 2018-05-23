//
//  ReportViewController.swift
//  StreamLine
//
//  Created by Colin Lockareff on 2/8/17.
//  Copyright © 2017 RRStudios. All rights reserved.
//

import UIKit
import CoreLocation


class ReportCell : UITableViewCell {
    
    var mapMarkerImage : UIImageView?
    var nameLabel : UILabel?
    var proximityLabel : UILabel?
    var disclosureInd : UIImageView?
    
    
    override init(style: UITableViewCellStyle, reuseIdentifier: String!)
    {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        
        //self.backgroundColor = UIColor(red: 134, green: 134, blue: 134, alpha: 100)
        
        mapMarkerImage = UIImageView(frame: CGRect(x: super.frame.minX + 10, y: super.frame.minY + 10, width: 30, height: 45))
        mapMarkerImage?.image = #imageLiteral(resourceName: "blackMapIcon")
        mapMarkerImage?.contentMode = UIViewContentMode.scaleToFill
        self.addSubview(mapMarkerImage!)
        
        nameLabel = UILabel(frame: CGRect(x: super.frame.minX + 50, y: super.frame.minY + 5, width: 320, height: 30))
        //nameLabel?.font = UIFont(name: "Noir_medium", size: 19)
        nameLabel?.font = nameLabel?.font.withSize(25)
        nameLabel?.textColor = UIColor(red: 223, green: 224, blue: 223, alpha: 100)
        self.addSubview(nameLabel!)
        
        proximityLabel = UILabel(frame: CGRect(x: super.frame.minX + 50, y: super.frame.minY + 45, width: 320, height: 15))
        //proximityLabel?.font = UIFont(name: "Noir_medium", size: 11)
        proximityLabel?.font = proximityLabel?.font.withSize(13)
        proximityLabel?.textColor = UIColor(red: 223, green: 224, blue: 223, alpha: 100)
        self.addSubview(proximityLabel!)
        
        disclosureInd = UIImageView(frame: CGRect(x: super.frame.maxX + 40, y: super.frame.minY + 25, width: 8, height: 15))
        disclosureInd?.image = #imageLiteral(resourceName: "disclosureIndicator")
        disclosureInd?.contentMode = UIViewContentMode.scaleToFill
        self.addSubview(disclosureInd!)
        
        self.selectionStyle = .gray
    }
    
    
    
    required init(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)!
    }
}


class ReportViewController: UIViewController, UITableViewDelegate, UITableViewDataSource, CLLocationManagerDelegate {
    
    // Local Variables
    var venueList : NSMutableArray = []
    var refreshControl: UIRefreshControl
    
    @IBOutlet weak var activityIndicator: NVActivityIndicatorView!
    @IBOutlet weak var venueTableView: UITableView!
    
    var locationManager: CLLocationManager!
    
    override func viewDidLoad()
    {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.

        venueTableView.register(ReportCell.self, forCellReuseIdentifier: "ReportCell")
        
        venueTableView.delegate = self
        venueTableView.dataSource = self
        venueTableView.isHidden = true
        
        venueTableView.isHidden = true
        activityIndicator.isHidden = false
        activityIndicator.startAnimating()
        
        if (CLLocationManager.locationServicesEnabled())
        {
            locationManager = CLLocationManager()
            locationManager.delegate = self
            locationManager.desiredAccuracy = kCLLocationAccuracyBest
            locationManager.requestWhenInUseAuthorization()
            locationManager.requestLocation()
        }
        
        refreshControl = {
            let refreshControl = UIRefreshControl()
            refreshControl.addTarget(self, action: #selector(self.handleRefresh(_:)), for: UIControlEvents.valueChanged)
            
            return refreshControl
        }()
        self.venueTableView.addSubview(self.refreshControl)
    }
    
    // number of rows in table view.. added one view for the last column that takes you to the google places search
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.venueList.count
    }
    
    // Load tableView with venueList
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ReportCell", for: indexPath) as! ReportCell
        //instantiate a cell type as google cell so that it will perform different functions
        
        let venue = (venueList[indexPath.row] as! Venue)
        
        cell.nameLabel?.text = venue.name
        
        cell.proximityLabel?.text = "\(round(100*venue.distanceToVenue)/100) miles away"
        
        cell.backgroundColor = UIColor.clear
        
        return cell
    }
    
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        
        let location = locations.last
        let userID = UserDefaults.standard.value(forKey: "userID") as! Int!
        
        if(userID != nil)
        {
            getVenues(nearLocation: location!, maxRange: 3.0, maxLineLength: 500, sortedBy: 0, withUserId: userID!, completion:
                {
                    (result: NSDictionary?, error: NSError?) -> () in
                    
                    if (result != nil)
                    {
                        self.venueList = result?.value(forKey: "venues") as! NSMutableArray
                    }
                    else
                    {
                        // Display no venues in range
    //                    self.venueList = self.hardcodedVenueList
                    }
                    
                    self.activityIndicator.stopAnimating()
                    self.activityIndicator.isHidden = true
                    self.venueTableView.reloadData()
                    self.venueTableView.isHidden = false
                    self.refreshControl.endRefreshing()
                })
        }
    }
    
    func locationManager(_ manager: CLLocationManager,
                         didFailWithError error: Error)
    {
        print(error)
    }

    func handleRefresh(_: UIRefreshControl) {
        if (CLLocationManager.locationServicesEnabled())
        {
            venueTableView.isHidden = true
            activityIndicator.isHidden = false
            activityIndicator.startAnimating()
            locationManager.requestLocation()
        }
    }
    
    func delay(_ delay:Double, closure:@escaping ()->()) {
        let when = DispatchTime.now() + delay
        DispatchQueue.main.asyncAfter(deadline: when, execute: closure)
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    let myLocation = CLLocation(latitude: 0, longitude: 0)
   
    @IBAction func reportPressed(_ sender: Any) {
        if (self.venueTableView.indexPathForSelectedRow?.row != nil)
        {
            
            let selectedVenue = self.venueList[(self.venueTableView.indexPathForSelectedRow?.row)!] as! Venue
            
            let storyboard = UIStoryboard(name: "Main", bundle: Bundle.main)
            let inLineView = storyboard.instantiateViewController(withIdentifier: "ReportingViewController") as! ReportingViewController
            
            inLineView.venue = selectedVenue
            
            let transition = CATransition()
            transition.duration = 0.25
            transition.type = kCATransitionPush
            transition.subtype = kCATransitionFromRight
            self.view.window!.layer.add(transition, forKey: kCATransition)
            self.show(inLineView, sender: self)
            
        }
        else {
            // create the alert
            let alert = UIAlertController(title: "No Venue Selected", message: "Please select a venue to report about its line!", preferredStyle: UIAlertControllerStyle.alert)
            
            // add an action (button)
            alert.addAction(UIAlertAction(title: "OK", style: UIAlertActionStyle.default, handler: nil))
            
            // show the alert
            self.present(alert, animated: true, completion: nil)
        }
    }

    
    @IBAction func searchPlacesPressed(_ sender: Any) {
        let storyboard = UIStoryboard(name: "Main", bundle: Bundle.main)
        let placesSearchView = storyboard.instantiateViewController(withIdentifier: "PlacesSearchViewController") as! PlacesSearchViewController
        
        let transition = CATransition()
        transition.duration = 0.25
        transition.type = kCATransitionPush
        transition.subtype = kCATransitionFromRight
        self.view.window!.layer.add(transition, forKey: kCATransition)
        self.show(placesSearchView, sender: self)

    }
    
    override init(nibName name: String!,bundle nibBundle: Bundle!)
    {
        venueList = []
        refreshControl = UIRefreshControl()
        super.init(nibName: name, bundle: nibBundle)
    }
    
    required init?(coder aDecoder: NSCoder) {
        venueList = []
        refreshControl = UIRefreshControl()
        super.init(coder: aDecoder)
    }
}

