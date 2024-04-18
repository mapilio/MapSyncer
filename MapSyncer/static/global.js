async function logout(event) {
        event.preventDefault();

        const { isConfirmed } = await Swal.fire({
            title: 'Are you sure?',
            text: 'Do you want to log out from all accounts?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, log out!',
            cancelButtonText: 'Cancel'
        });
        if (isConfirmed) {
            try {
                const sessionResponse = await fetch('/remove-accounts');
                const sessionData = await sessionResponse.json();

                if (sessionData.success) {
                    console.log("Flask session cleared");

                    localStorage.clear();
                    console.log("localStorage cleared");

                    document.cookie.split(";").forEach(function(c) {
                        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
                    });
                    console.log("Cookies cleared");

                    window.location.reload();
                } else {
                    console.log("Error clearing Flask session");
                }
            } catch (error) {
                console.log("Error:", error);
            }
        }
    }