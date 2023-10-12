import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Like({
  handleClick,
  numlike,
  likestatus,
  likeurl,
  postid,
}) {
  console.log(numlike, likestatus);
  return (
    <div>
      <p>
        {numlike} {numlike === 0 || numlike > 1 ? "likes" : "like"}
      </p>
      <p>
        {postid && (
          <button
            onClick={() => handleClick(numlike, likestatus, likeurl, postid)}
            data-testid="like-unlike-button"
          >
            {likestatus ? "un" : ""}like
          </button>
        )}
      </p>
    </div>
  );
}

//<img src={imgUrl} alt="post_image" className="post_img" onDoubleClick={handleDoubleClick}/>
//<Like handleClick = {handleClick} numlike = {numlike} likestatus = {likestatus}/>
Like.propTypes = {
  handleClick: PropTypes.func,
  numlike: PropTypes.number,
  likestatus: PropTypes.bool,
  likeurl: PropTypes.string,
  postid: PropTypes.number,
};
/*
const [postid, setPostId] = useState(0);
  const [numlike, setNumLike] = useState(0);
  const [likestatus,setLikeStatus] = useState(false);
  const [likeurl, setLikeUrl] = useState("");

  const handleClick = async ()=>{
    fetch(likestatus ? likeurl : `/api/v1/likes/?${new URLSearchParams({
        'postid': postid
    })}`, {
        credentials: "same-origin", 
        method: likestatus ? "DELETE" : "POST", 
    })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      if (response.status === 201)
      return response.json();
      else return null;
    })
    .then((data) => {
      // To be fixed : ignoreStaleRequest
        if(data)
        setLikeUrl(data.url); 
    })
    .catch((error) => console.log(error));
    likestatus? setLikeStatus(!likestatus)|| setNumLike(numlike-1) 
              : setLikeStatus(!likestatus)|| setNumLike(numlike+1) ;
  };
  async function handleDoubleClick (){
    if(!likestatus){
        setNumLike(numlike+1);
        setLikeStatus(!likestatus);
        fetch(`/api/v1/likes/?${new URLSearchParams({
            'postid': postid
        })}`, {
            credentials: "same-origin", 
            method: "POST", 
        })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          if (response.status === 201)
          return response.json();
          else return null;
        })
        .then((data) => {
            // To be fixed : ignoreStaleRequest
            if(data)
            setLikeUrl(data.url); 
        })
        .catch((error) => console.log(error));
    }
  };
*/
/*
setPostId(data.postid);
          setLikeStatus(data.likes.lognameLikesThis);
          setLikeUrl(data.likes.url);
          setNumLike(data.likes.numLikes);
*/
