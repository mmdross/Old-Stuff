//
//  LoginViewController.swift
//  Garrett Zelin
//


import UIKit
import Alamofire
import FacebookLogin
import FBSDKCoreKit
import FBSDKLoginKit

class LoginViewController: UIViewController, FBSDKLoginButtonDelegate {

    
    @IBOutlet weak var signUpButton: UIButton!
    @IBOutlet weak var errorLog: UILabel!
    @IBOutlet var username_input: UITextField!
    @IBOutlet var password_input: UITextField!
    @IBOutlet var login_button: UIButton!
    
    var login_session:String = ""
    var fbLoginSuccess = false

    
    override func viewDidLoad() {
        super.viewDidLoad()
        viewWillAppear(true)
        self.view.backgroundColor = UIColor(patternImage: UIImage(named: "Club queue Copy.png")!)
        
        self.hideKeyboardWhenTappedAround()
        
        let loginButton = FBSDKLoginButton()
        loginButton.center = view.center
        
        view.addSubview(loginButton)
        
        loginButton.frame = CGRect(x: 16, y: 496, width: view.frame.width - 32, height: 50)
        
        loginButton.delegate = self

    }
    
    func loginButtonDidLogOut(_ loginButton: FBSDKLoginButton!) {
        print("Did log out of Facebook")
    }
    
    
    
    func loginButton(_ loginButton: FBSDKLoginButton!, didCompleteWith result: FBSDKLoginManagerLoginResult!, error: Error!) {
        
        if ((error) != nil) {
            // Process error
            print(error)
            return
        }
        else if result.isCancelled {
            // Handle cancellations
        }
        else {
            fbLoginSuccess = true
            // If you ask for multiple permissions at once, you
            // should check if specific permissions missing

            var data:[String:AnyObject]!
            
            let parameters2: Parameters = ["email": FBSDKAccessToken.current().userID, "password": FBSDKAccessToken.current().userID]
            
            //        1: username doesn’t exist
            //        2: wrong password
            
            Alamofire.request("https://aqueous-retreat-35345.herokuapp.com/api/login", method: .get, parameters: parameters2).responseJSON { (response2:DataResponse<Any>) in
                
                let testdata2 = response2.result.value as! NSArray
                
                let success2 = testdata2[0] as! Bool
                var dataResponse = testdata2[1] as! Int
                print("Facebook User UserID", dataResponse)

                if(success2 == false && dataResponse == 1)// doesn't exist so create one
                {
                    FBSDKGraphRequest(graphPath: "me", parameters: ["fields": "first_name, last_name"]).start(completionHandler: { (connection, result, error) -> Void in
                        print("Facebook Graph Request")
                        if (error == nil){
                            data = result as! [String : AnyObject]
                            let parameters3: Parameters = ["email": FBSDKAccessToken.current().userID, "password": FBSDKAccessToken.current().userID, "firstname":  data["first_name"]!, "lastname":  data["last_name"]!]

                            Alamofire.request("https://aqueous-retreat-35345.herokuapp.com/api/register", method: .get, parameters: parameters3).responseJSON { (response:DataResponse<Any>) in
                                let testdata = response.result.value as! NSArray
                                print(testdata[0],testdata[1])
                                let success = testdata[0] as! Bool
                                dataResponse = testdata[1] as! Int
                                print("Registering Facebook User with UserID ", dataResponse)
                                UserDefaults.standard.setValue(dataResponse, forKey: "userID")
                                self.performSegue(withIdentifier: "Four", sender: self)
                            }
                        }
                        else
                        {
                            print(error!, connection!)
                        }
                       
                    })
                    print("Facebook Graph Request End")
                }
                else {
                    UserDefaults.standard.setValue(dataResponse, forKey: "userID")
                    self.performSegue(withIdentifier: "Four", sender: self)
                }
                
            }
        }
    }
    
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(false)
        //UserDefaults.standard.setValue(nil, forKey: "userID") //DELETE!
        let defaultUserID = UserDefaults.standard.value(forKey: "userID")
        
        if(defaultUserID != nil) //Logged In
        {
            self.view.isHidden = true
            self.performSegue(withIdentifier: "Four", sender: self)
        }
    
//        if (FBSDKAccessToken.current() != nil) //Don't Uncomment!
//        {
//            self.performSegue(withIdentifier: "Four", sender: self)
//        }

    }

    
    @IBAction func clickLogin(_ sender: Any) {
        login_now(username: username_input.text!, password: password_input.text!)
    }
    

    
    

    
    func login_now(username:String, password:String)
    {
        //user_1 pw1
        let parameters1: Parameters = ["email": username, "password": password]
        
//        1: username doesn’t exist
//        2: wrong password
        Alamofire.request("https://aqueous-retreat-35345.herokuapp.com/api/login", method: .get, parameters: parameters1).responseJSON { (response:DataResponse<Any>) in
            
            let testdata = response.result.value as! NSArray
            let success = testdata[0] as! Bool
            let response = testdata[1] as! Int
            var userID: Int
            
            if(success == true)//Successfull Login
            {
                userID = response
                self.errorLog.text = "Login Successful" 
                UserDefaults.standard.setValue(userID, forKey: "userID") //Sets the session
                self.performSegue(withIdentifier: "Four", sender: self)
                
                
            } else if(response == 1) { // 1: username doesn’t exist
                
                self.errorLog.text = "Username Does Not Exist"
                
            } else if(response == 2) { // 2: wrong password
                
                self.errorLog.text = "Incorrect Password"
                
            } else {
            
                print("Alamofire Error")
            }
        }
    }
}





