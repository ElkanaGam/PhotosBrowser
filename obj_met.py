note for next day: - > 9.9

*create 'test' object / mode that will assign all fields 
beforehead
* check that every part is first clear all fields


done

note for 13.9

* 2 files: 
Browser -> replace to add dir dialog, clear the enterise[1]
BrowserAndSearch -> replace to add dir dialog, clear the enterise[1]
                 -> add tag lables, add save function, add seaech function (interface style)
                 separete the insertion of the number of dirs. and then the screen  remain the same, and the get dir
                 short commands:
                 get_dir
                 get_number
                 
                 
note for 15-16-17.9:

* change prot to testing - done
* test runing every window seperatly
* use click to pass window name
* update the browser file from 
* create dir for testin with 2 oratanion photos - done
* crete git, git ignor push the browser

note for 20-21.9
* update browser file
* git ignore push the project to git repository
* run all 
* hande num dir = ''


note for 24-25.9:

*Browser: 
    fonts andbackground 
    orgnize function
    init - look for unneccesary fields
    use the config data
    
    -> open issue : <-
    if user insert 2 same dir names ut will couse index out of range err
    whke drawing resukts table. becouse TOTAL dict wil contain lee keys than num_of_dir:
    sulotion 1:
    in draw table:
        if len(total_values) < num_of_dir +1:
            duolicate values
    solution 2:
    names = set{trash}
    after user insert the names check len names == num of dir 
        if smaller:
            err msg, return to previous screen 
            