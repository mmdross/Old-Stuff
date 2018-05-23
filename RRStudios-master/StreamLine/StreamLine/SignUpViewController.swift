//
//  LoginViewController.swift
//  Garrett Zelin
//


import UIKit
import Alamofire

class SignUpViewController: UIViewController {
    
    @IBOutlet weak var firstName: UITextField!
    
    @IBOutlet weak var lastName: UITextField!

    @IBOutlet weak var email: UITextField!
    
    @IBOutlet weak var password: UITextField!
    
    @IBAction func signUpClick(_ sender: UIButton) {
        
        signup_now(email: email.text!, password: password.text!, firstName: firstName.text!, lastName: lastName.text!)
    }
    
    @IBOutlet weak var errorLog: UILabel!

    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.view.backgroundColor = UIColor(patternImage: UIImage(named: "Club queue Copy.png")!)
        
        self.hideKeyboardWhenTappedAround()
    }
    
    
    
    
    
    
    func signup_now(email:String, password:String, firstName:String, lastName:String)
    {
        //user_1 pw1
        let parameters1: Parameters = ["email": email, "password": password, "firstname": firstName, "lastname": lastName ]
        
        //        1: username doesn’t exist
        //        2: wrong password
        Alamofire.request("https://aqueous-retreat-35345.herokuapp.com/api/register", method: .get, parameters: parameters1).responseJSON { (response:DataResponse<Any>) in
            
            let testdata = response.result.value as! NSArray
            print(testdata[0],testdata[1])
            let success = testdata[0] as! Bool
            let response = testdata[1] as! Int
            var userID: Int
            
            if(success)//Successfull Login
            {
                //self.errorLog.text = "Succesful Login!"
                userID = response
                UserDefaults.standard.setValue(userID, forKey: "userID") //Sets the session
                
                //presentViewController(nextViewController, animated: true, completion: nil)
                self.performSegue(withIdentifier: "signUpToOnboard", sender: self)
                
//                let secondViewController = self.storyboard?.instantiateViewController(withIdentifier: "MainTabViewController") as! UITabBarController
//                self.navigationController?.pushViewController(secondViewController, animated: true)
                
            } else if(response == 1) { // 1: username already exists
                
                self.errorLog.text = "Username Already Exists"
                
            } else {
                
                print("Alamofire Error")
            }
        }
    }
}







