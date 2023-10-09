import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import Post from "./post";
import InfiniteScroll from "react-infinite-scroll-component";


export default function PostList({ url }) {
    const [posts, setPosts] = useState([]);
    const [next, setNext] = useState("");
    const [hasMore, setHasMore] = useState(true);

    // Used as the 'next' callback for the InfiniteScroll component
    const fetchMoreData = () => {
        setTimeout(() => {
            let ignoreStaleRequest = false;
            fetch(next, { credentials: "same-origin" })
                .then((response) => {
                    if (!response.ok) throw Error(response.statusText);
                    return response.json();
                })
                .then((data) => {
                    if (!ignoreStaleRequest) {
                        setPosts([...posts, ...data.results]);
                        setNext(data.next);
                        setHasMore(Boolean(data.next.length));
                        console.log(data)
                    }
                })
                .catch((error) => console.log(error));
            
            return () => {
                ignoreStaleRequest = true;
            };
        }, 1000);
    };


    useEffect(() => {
        let ignoreStaleRequest = false;
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                if (!ignoreStaleRequest) {
                    setPosts([...data.results]);
                    setNext(data.next);
                    setHasMore(Boolean(data.next.length));
                    console.log(data.next)
                }
            })
            .catch((error) => console.log(error));
        
        return () => {
            ignoreStaleRequest = true;
        };
    }, [url]);

    return (
        <div>
            <InfiniteScroll
                dataLength={posts.length} //This is important field to render the next data
                next={fetchMoreData}
                hasMore={hasMore}
                loader={<h4 style={{ textAlign: 'center' }}>Loading...</h4>}
                endMessage={
                    <p style={{ textAlign: 'center' }}>
                    <b>Yay! You have seen it all</b>
                    </p>
                }
                >
                    { posts?.map((post) =>
                        <Post 
                            key={post.postid}
                            {...post}
                        />
                    )}
            </InfiniteScroll>     
        </div>
    );
}

PostList.propTypes = {
    url: PropTypes.string.isRequired,
};