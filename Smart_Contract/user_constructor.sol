pragma solidity ^0.4.24;

contract userWithConstructor {

    address public owner;
    bytes32 biohash;
    mapping(address=>uint) whitelist;
    address private authority= 0x64a20b6347347444a970C5B8ad099125C3f01EbD;
    bool enabled=true;

    constructor (address user,bytes32 hash) public {
        require(msg.sender==authority,"You don't have access to create a contract");
        owner=user;
        biohash=hash;
    }


    // function setup (address user, bytes32 hash) public {
    //     require(msg.sender == authority,"You don't have access to create a contract");
    //     owner=user;
    //     biohash=hash;
    // }

    function revoke () public{
        require(msg.sender==authority,"You don't have access to revoke the contract");
        enabled=false;
    }

    function authorize(address user,uint valid_time) public {
        require(msg.sender==owner,"You don't have access to authorize");
        require(enabled==true,"The contract is revoked");
        whitelist[user]=now+valid_time;
    }

    function retrieve() public constant returns (bytes32){
        require(whitelist[msg.sender]!=0,"You don't have access to retrive");
        require(whitelist[msg.sender]>now,"The access has expired");
        require(enabled==true,"The contract is revoked");
        return biohash;
    }

    function get_auth() public constant returns (address){
        require(whitelist[msg.sender]!=0,"You don't have access to get authority");
        require(whitelist[msg.sender]>now,"The access has expired");
        require(enabled==true,"The contract is revoked");
        return authority;
    }


}
