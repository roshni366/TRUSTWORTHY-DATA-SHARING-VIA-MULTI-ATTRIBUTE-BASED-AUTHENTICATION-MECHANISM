pragma solidity >= 0.4.0 <= 0.9;
pragma experimental ABIEncoderV2;
//Authentication solidity code
contract Authentication {

    uint public authCount = 0; 
    mapping(uint => auth) public authList; 
     struct auth
     {
       string auth_hash;
       string requester;
     }
 
   // events 
   event authCreated(uint indexed _authId);
   
   //function  to save auth details to Blockchain
   function saveAuthentication(string memory hd, string memory req) public {
      authList[authCount] = auth(hd, req);
      emit authCreated(authCount);
      authCount++;
    }

     //get authentication count
    function getAuthenticationCount()  public view returns (uint) {
          return  authCount;
    }

     function getAuthentication(uint i) public view returns (string memory) {
        auth memory hl = authList[i];
	return hl.auth_hash;
    }

     function getRequester(uint i) public view returns (string memory) {
        auth memory hl = authList[i];
	return hl.requester;
    } 
	
 uint public userCount = 0; 
    mapping(uint => user) public usersList; 
     struct user
     {
       string username;
       string password;
       string phone;
       string email;
       string user_address;
       string usertype;
     }
 
   // events
 
   event userCreated(uint indexed _userId);
 
  function createUser(string memory _username, string memory _password, string memory _phone, string memory _email, string memory _address, string memory ut) public {
      usersList[userCount] = user(_username, _password, _phone, _email, _address, ut);
      emit userCreated(userCount);
      userCount++;
    }

    
     //get user count
    function getUserCount()  public view returns (uint) {
          return  userCount;
    }

    function getUsername(uint i) public view returns (string memory) {
        user memory usr = usersList[i];
	return usr.username;
    }

    function getPassword(uint i) public view returns (string memory) {
        user memory usr = usersList[i];
	return usr.password;
    }

    function getAddress(uint i) public view returns (string memory) {
        user memory usr = usersList[i];
	return usr.user_address;
    }

    function getEmail(uint i) public view returns (string memory) {
        user memory usr = usersList[i];
	return usr.email;
    }

    function getPhone(uint i) public view returns (string memory) {
        user memory usr = usersList[i];
	return usr.phone;
    }
    
    function getUserType(uint i) public view returns (string memory) {
        user memory usr = usersList[i];
	return usr.usertype;
    }

     uint public ownerCount = 0; 
    mapping(uint => owner) public ownerList; 
     struct owner
     {
       string owner_details;
       string ownername;
     }
 
   // events 
   event ownerCreated(uint indexed _ownerId);
   
   //function  to save owner details to Blockchain
   function saveOwner(string memory od, string memory on) public {
      ownerList[ownerCount] = owner(od, on);
      emit ownerCreated(ownerCount);
      ownerCount++;
    }

     //get owner count
    function getOwnerCount()  public view returns (uint) {
          return ownerCount;
    }

     function getDetails(uint i) public view returns (string memory) {
        owner memory hl = ownerList[i];
	return hl.owner_details;
    }

     function getOwnername(uint i) public view returns (string memory) {
        owner memory hl = ownerList[i];
	return hl.ownername;
    } 

}