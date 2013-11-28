var change_listeners = [];

function VolumeListCtrl($scope, $http) {
    $scope.loadData = function () {
        $http.get('/volumes').success(function(data) {
            console.log(data);
            $scope.volumes = data;
        });
    };

    //initial load
    $scope.loadData();
    
    // Register as listener
    change_listeners.push($scope.loadData);

    // setInterval(function(){$scope.loadData();}, 1000);
}


function ws_on_msg(data){
    console.log("Change detected");
    for(var i=0; i<change_listeners.length; i++) {
        change_listeners[i]();
    }
}
