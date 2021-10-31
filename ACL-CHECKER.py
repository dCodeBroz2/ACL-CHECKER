import netmiko
import sys
import os

def checker(ipAdr,devType):

  if devType == "??":
    devType = "huawei"
    bestPF = "??.txt"
    cmdRun = "display acl all"
  elif devType == "!!":
    devType = "cisco_ios"
    bestPF = "!!.txt"
    cmdRun = "show access-list"
  elif devType == "##":
    devType = "cisco_ios"
    bestPF = "##.txt"
    cmdRun = "show access-list"
  else:
    exit("WHAT?????")
  try:
    dev =  { 
    'host':ipAdr,
    'device_type':devType,
    'username':"??",
    'password':"??",
    'fast_cli': False
    }

    conn = netmiko.ConnectHandler(**dev)

    deviceACL = conn.send_command(cmdRun)
    
    if len(deviceACL) > 0:
      path = os.path.join(ipAdr, f"{ipAdr}_ACL.txt")
      with open(path,"w") as tempFile:
        tempFile.write(deviceACL)

      conn.disconnect()

      with open(bestPF,"r") as file:
        fileLines = file.readlines()

        for item in fileLines:
          mainItem = item.strip()
          if "@" in mainItem:
            mainItem = mainItem.split('@',2)[1]
          if "(" in mainItem:
            mainItem = mainItem.split('(',1)[0]
          
          main2 = mainItem

          # if 'Standard' in item or 'Extended' in item:
          if 'permit' not in item and 'deny' not in item:
            path = os.path.join(ipAdr, f"{ipAdr}_ACL-FAILED.txt")
            with open(path,"a") as result:
              result.write(f"\n{item}")

          if "permit" in main2:
            main2 = main2[main2.rfind("permit"):]
          elif "deny" in main2:
            main2 = main2[main2.rfind("deny"):]
          
          bestPracLine = main2
          
          path = os.path.join(ipAdr, f"{ipAdr}_ACL.txt")
          with open(path,"r") as devACLList:
            objdevACLList = devACLList.readlines()

          # for item in objdevACLList:
          for i in range(0,len(objdevACLList)):
            item = objdevACLList[i]
            tempItem = item.strip()
            main2 = tempItem.split('(',1)[0]

            if "permit" in main2:
              main2 = main2[main2.rfind("permit"):]
            elif "deny" in main2:
              main2 = main2[main2.rfind("deny"):]

            # input(f"acl line converted from {tempItem} to : {main2}")
            objdevACLList[i] = main2
            # input(f"main item is now : {objdevACLList[i]}")
            i = i + 1

          # Space cleaning
          if '  ' in bestPracLine:
            for i in range(1,6):
              bestPracLine = bestPracLine.replace('  ',' ')
          
          for item in objdevACLList:
            if '  ' in item:
              for i in range(1,6):
                item.replace('  ',' ')

   
          if bestPracLine in objdevACLList:
            # input("EQUAL!")
            delParam = [i for i, e in enumerate(objdevACLList) if e == bestPracLine]
            if len(delParam) > 0:
              # print(f"removed from device ACLs {objdevACLList[int(delParam[0])]}")
              objdevACLList.pop(int(delParam[0]))
            
            pass
          else:
            # input("NOT EQUAL!")
            if 'permit' in bestPracLine or 'deny' in bestPracLine:
              path = os.path.join(ipAdr, f"{ipAdr}_ACL-FAILED.txt")
              with open(path,"a") as result:
                result.write(f"[-]FAILED : {mainItem}\n")
    else:
      input("ACL NOT ACCESSIBLE!")    
              
  except Exception as e:
    print(f"Exception : {e}")
  
def cleaner(fileLines):
  tempList = []

  for item in fileLines:
    mainItem = item.strip()
    if "@" in mainItem:
      mainItem = mainItem.split('@',2)[1]
    if "(" in mainItem:
      mainItem = mainItem.split('(',1)[0]
    
    if "permit" in mainItem:
      mainItem = mainItem[mainItem.rfind("permit"):]
    elif "deny" in mainItem:
      mainItem = mainItem[mainItem.rfind("deny"):]

    bestPracLine = mainItem
    tempList.append(bestPracLine)
  
  return tempList


def revChecker(ipAdr,devType):
  bestPF = devType+".txt"
  orgIP = ipAdr
  ipAdr = ipAdr+"_ACL.txt"

  try:
    path = os.path.join(orgIP, ipAdr)
    with open(bestPF,"r") as file, open(path,"r") as target:
      fileLines = file.readlines()
      deviceACL = target.readlines()

      fileLines = cleaner(fileLines)
      deviceACL = cleaner(deviceACL)

      # diffDict = set(fileLines) ^ set(deviceACL)
      for item in deviceACL:
        # if 'Standard' in item or 'Extended' in item:
        if 'permit' not in item and 'deny' not in item:
          path = os.path.join(orgIP, f"{ipAdr}_ACL-MORE.txt")
          with open(path,"a") as result:
            result.write(f"\n{item}")

        # Space cleaning
        if '  ' in item:
          for i in range(1,6):
            item.replace('  ',' ')
        
        for item2 in fileLines:
          if '  ' in item2:
            for i in range(1,6):
              item2.replace('  ',' ')

        if item not in fileLines:
          path = os.path.join(orgIP, f"{ipAdr}_ACL-MORE.txt")
          with open(path,"a") as result:
            result.write(f"[-]MORE RULES => {item}\n")

        delParam = [i for i, e in enumerate(fileLines) if e == item]
        if len(delParam) > 0:
          # print(f"removed from best practice {fileLines[int(delParam[0])]}")
          fileLines.pop(int(delParam[0]))
                
  except Exception as e:
    print(f"Exception : {e}")

def main():
  ipAdr = sys.argv[1]
  bestPF = sys.argv[2]

  try:
    os.mkdir(ipAdr)
  except:
    pass

  checker(ipAdr,bestPF)
  revChecker(ipAdr,bestPF)
  
main()
